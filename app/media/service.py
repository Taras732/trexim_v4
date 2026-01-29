"""
Media service - handles image upload to Cloudinary with optimization
"""
import os
import uuid
from typing import Optional
from urllib.parse import urlparse
from fastapi import UploadFile
import cloudinary
import cloudinary.uploader

# Configure Cloudinary - support both individual vars and CLOUDINARY_URL
cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
api_key = os.environ.get("CLOUDINARY_API_KEY")
api_secret = os.environ.get("CLOUDINARY_API_SECRET_KEY") or os.environ.get("CLOUDINARY_API_SECRET")

# Fallback to CLOUDINARY_URL if individual vars not set
if not all([cloud_name, api_key, api_secret]):
    cloudinary_url = os.environ.get("CLOUDINARY_URL")
    if cloudinary_url:
        parsed = urlparse(cloudinary_url)
        cloud_name = parsed.hostname
        api_key = parsed.username
        api_secret = parsed.password

if all([cloud_name, api_key, api_secret]):
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    print(f"Cloudinary configured: cloud={cloud_name}, api_key={api_key[:4]}***, api_secret=set")
else:
    print(f"WARNING: Cloudinary not configured! cloud={cloud_name}, api_key={api_key}, api_secret={'set' if api_secret else 'NOT SET'}")

# Configuration
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def upload_image(
    file: UploadFile,
    category: str = "blog"
) -> dict:
    """
    Upload image to Cloudinary with automatic optimization
    
    Args:
        file: Uploaded file
        category: Category folder (blog, icons, etc.)
    
    Returns:
        dict with URLs for original, optimized, and thumbnail versions
    
    Raises:
        ValueError: If file type not allowed or file too large
    """
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise ValueError(f"File type not allowed. Allowed: {', '.join(ALLOWED_TYPES)}")
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Generate unique public ID
    file_id = uuid.uuid4().hex[:12]
    public_id = f"{category}/{file_id}"
    
    try:
        # Upload to Cloudinary with transformations
        upload_result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            folder=category,
            format="webp",  # Convert to WebP
            quality="auto",  # Automatic quality optimization
            fetch_format="auto",  # Automatic format selection
            width=1920,  # Max width
            crop="limit",  # Only resize if larger
            eager=[
                {"width": 400, "height": 400, "crop": "fill", "quality": 80, "format": "webp"},  # Thumbnail
            ],
            eager_async=False  # Generate transformations immediately
        )
        
        # Get URLs from Cloudinary
        base_url = upload_result['secure_url']
        
        # Construct thumbnail URL (first eager transformation)
        thumbnail_url = upload_result.get('eager', [{}])[0].get('secure_url', base_url)
        
        return {
            "id": file_id,
            "public_id": upload_result['public_id'],
            "original": base_url,
            "optimized": base_url,  # Cloudinary already optimized
            "thumbnail": thumbnail_url
        }
    
    except Exception as e:
        raise ValueError(f"Upload failed: {str(e)}")


def delete_image(public_id: str) -> bool:
    """
    Delete image from Cloudinary
    
    Args:
        public_id: Cloudinary public ID
    
    Returns:
        True if deleted, False if not found
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception:
        return False


def get_image_url(
    public_id: str,
    variant: str = "optimized",
    width: Optional[int] = None,
    height: Optional[int] = None
) -> str:
    """
    Get URL for an image with optional transformations
    
    Args:
        public_id: Cloudinary public ID
        variant: 'original', 'optimized', or 'thumbnail'
        width: Optional width transformation
        height: Optional height transformation
    
    Returns:
        URL string with transformations applied
    """
    transformations = {"format": "webp", "quality": "auto"}
    
    if variant == "thumbnail":
        transformations.update({"width": 400, "height": 400, "crop": "fill"})
    elif variant == "optimized":
        transformations.update({"width": 1920, "crop": "limit"})
    
    if width:
        transformations["width"] = width
    if height:
        transformations["height"] = height

    return cloudinary.CloudinaryImage(public_id).build_url(**transformations)
