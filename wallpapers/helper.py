from cloudinary.utils import cloudinary_url

def get_resized_urls(public_id):
    resolutions = {
        "HD (1920x1080)": {"width": 1920, "height": 1080, "crop": "fill"},
        "2K (2560x1440)": {"width": 2560, "height": 1440, "crop": "fill"},
        "4K (3840x2160)": {"width": 3840, "height": 2160, "crop": "fill"},
        "Mobile (1080x2400)": {"width": 1080, "height": 2400, "crop": "fill"},
    }
    urls = {}
    for label, options in resolutions.items():
        url, _ = cloudinary_url(public_id, transformation=[options])
        urls[label] = url
    return urls
