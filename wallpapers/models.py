from django.db import models
from django.utils.text import slugify

class Wallpaper(models.Model):
    CATEGORY_CHOICES = [
        ('nature', 'Nature'),
        ('cityscape', 'Cityscape'),
        ('space', 'Space'),
        ('fantasy', 'Fantasy'),
        ('games', 'Games'),
        ('anime', 'Anime'),
        ('cars', 'Cars'),
        ('technology', 'Technology'),
        ('movies', 'Movies'),
        ('superheros', 'Super Heroes'),
        ('other', 'Other')
    ]

    DEVICE_CHOICES = [
        ('pc', 'PC'),
        ('mobile', 'Mobile')
    ]

    title = models.CharField(
        max_length=255,
        help_text="Descriptive title for the wallpaper"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="Automatically generated from title"
    )
    drive_file_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Google Drive file ID"
    )
    view_link = models.URLField(
        help_text="URL for viewing the image"
    )
    download_link = models.URLField(
        help_text="URL for downloading the image"
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME type of the image file"
    )
    width = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Image width in pixels"
    )
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Image height in pixels"
    )
    size_bytes = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        choices=CATEGORY_CHOICES,
        help_text="Category of the wallpaper"
    )
    resolution_label = models.CharField(
        max_length=50,
        blank=True,
        editable=False,
        help_text="Auto-generated resolution label (e.g. '4K')"
    )
    downloads = models.PositiveIntegerField(
        default=0,
        help_text="Number of downloads"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when uploaded"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when last updated"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark as featured wallpaper"
    )
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated tags for better discoverability"
    )
    device = models.CharField(
        default='pc',
        choices=DEVICE_CHOICES,
        help_text="Device for this wallpaper"
    )
    

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Wallpaper"
        verbose_name_plural = "Wallpapers"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
            models.Index(fields=['downloads']),
            models.Index(fields=['device']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1
            while Wallpaper.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug

        if self.width and self.height:
            self.resolution_label = self.generate_resolution_label()
        
        super().save(*args, **kwargs)


    def generate_resolution_label(self):
        """Generate human-readable resolution label"""
        if self.width >= 7680 or self.height >= 4320:
            return "8K"
        elif self.width >= 3840 or self.height >= 2160:
            return "4K"
        elif self.width >= 2560 or self.height >= 1440:
            return "QHD"
        elif self.width >= 1920 or self.height >= 1080:
            return "FHD"
        elif self.width >= 1280 or self.height >= 720:
            return "HD"
        return f"{self.width}x{self.height}"

    def increment_downloads(self):
        """Increment download counter"""
        self.downloads += 1
        self.save(update_fields=['downloads'])

    @property
    def aspect_ratio(self):
        """Return aspect ratio as string (e.g. '16:9')"""
        if not self.width or not self.height:
            return None
            
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
            
        divisor = gcd(self.width, self.height)
        return f"{self.width//divisor}:{self.height//divisor}"