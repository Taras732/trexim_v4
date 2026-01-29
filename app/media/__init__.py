"""
Media module - image upload, conversion, optimization
"""
# CRITICAL: Configure Cloudinary BEFORE any imports of cloudinary library
import os
from urllib.parse import urlparse

# Parse CLOUDINARY_URL and set individual environment variables
# This MUST happen before cloudinary module is imported anywhere
cloudinary_url = os.environ.get("CLOUDINARY_URL")
if cloudinary_url:
    parsed = urlparse(cloudinary_url)
    os.environ["CLOUDINARY_CLOUD_NAME"] = parsed.hostname or ""
    os.environ["CLOUDINARY_API_KEY"] = parsed.username or ""
    os.environ["CLOUDINARY_API_SECRET"] = parsed.password or ""
    print(f"Cloudinary configured: {parsed.hostname}")
else:
    print("WARNING: CLOUDINARY_URL not set")

# NOW import service functions (cloudinary will read the env vars we just set)
from .service import upload_image, delete_image, get_image_url

__all__ = ["upload_image", "delete_image", "get_image_url"]
