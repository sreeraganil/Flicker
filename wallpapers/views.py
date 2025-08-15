from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.text import slugify
from .models import Wallpaper
import cloudinary.uploader
import requests
from django.contrib import messages

def home(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()
    res = request.GET.get("res", "").strip()
    
    qs = Wallpaper.objects.all().order_by('-created_at')
    
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | 
            Q(category__icontains=q) |
            Q(tags__icontains=q)
        )
    if cat:
        qs = qs.filter(category__iexact=cat)
    if res:
        if res.lower() == '4k':
            qs = qs.filter(width__gte=3840) | qs.filter(height__gte=2160)
        elif res.lower() == '8k':
            qs = qs.filter(width__gte=7680) | qs.filter(height__gte=4320)
        else:
            qs = qs.filter(resolution_label__iexact=res)
    
    paginator = Paginator(qs, 24)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)
    
    return render(
        request, 
        "wallpapers/home.html", 
        {
            "page_obj": page_obj, 
            "q": q, 
            "cat": cat, 
            "res": res,
            "categories": Wallpaper.CATEGORY_CHOICES
        }
    )

def download(request, slug):
    wp = get_object_or_404(Wallpaper, slug=slug)
    wp.increment_downloads()
    
    # For Cloudinary downloads, we might want to force download with specific transformations
    download_url = f"{wp.download_link.replace('/upload/', '/upload/fl_attachment/')}"
    
    response = requests.get(download_url, stream=True)
    file_extension = wp.mime_type.split('/')[-1] if wp.mime_type else 'jpg'
    filename = f"{slugify(wp.title)}.{file_extension}"

    response = HttpResponse(
        response.content, 
        content_type=f"application/{file_extension}"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def upload(request):
    if request.method == "POST":
        # --- Manual Data Retrieval ---
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "")
        image_file = request.FILES.get("image")

        # --- Manual Validation ---
        if not title or not image_file:
            messages.error(request, "Title and Image file are required.")
            return redirect("wallpapers:upload") # Or render the form again

        try:
            # Upload to Cloudinary with optimization
            uploaded = cloudinary.uploader.upload(
                image_file,
                folder="wallpapers",
                resource_type="image",
                quality="auto:best",
                # format="auto" # Let Cloudinary decide the best format
            )

            # Get image metadata from Cloudinary's response
            width = uploaded.get("width")
            height = uploaded.get("height")
            size_bytes = uploaded.get("bytes", 0)
            img_format = uploaded.get("format", "")

            # Fallback to get dimensions if Cloudinary fails to provide them
            if not width or not height:
                try:
                    image_file.seek(0)
                    with Image.open(image_file) as img:
                        width, height = img.size
                except Exception as e:
                    print(f"Pillow error getting image dimensions: {e}")

            # Create the wallpaper instance
            wp = Wallpaper(
                title=title,
                category=category,
                drive_file_id=uploaded["public_id"],
                view_link=uploaded["secure_url"],
                download_link=uploaded["secure_url"],
                mime_type=f"image/{img_format}",
                width=width,
                height=height,
                size_bytes=size_bytes,
                is_featured=False
            )
            
            wp.save() # This will auto-generate slug and resolution_label
            
            messages.success(request, f"'{wp.title}' uploaded successfully!")
            return redirect("wallpapers:detail", slug=wp.slug)
        
        except Exception as e:
            messages.error(request, f"An error occurred during upload: {str(e)}")

    # For a GET request, just render the page
    return render(
        request, 
        "wallpapers/upload.html", 
        {
            "max_size_mb": 20 # For displaying in the template
        }
    )


def detail(request, slug):
    wp = get_object_or_404(Wallpaper, slug=slug)
    
    # Get related wallpapers (same category)
    related = Wallpaper.objects.filter(
        category=wp.category
    ).exclude(
        slug=wp.slug
    ).order_by('-downloads')[:6]
    
    return render(
        request, 
        "wallpapers/detail.html", 
        {
            "wp": wp,
            "related": related,
            "aspect_ratio": wp.aspect_ratio
        }
    )