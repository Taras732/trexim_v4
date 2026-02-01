"""
Media API - endpoints for image upload and management
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from ..media import upload_image, delete_image

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    category: str = Query(default="blog", description="Category: blog, icons, etc.")
):
    """
    Upload image file

    - Accepts: PNG, JPG, JPEG, GIF, WebP
    - Max size: 10MB
    - Auto-converts to WebP
    - Creates thumbnail

    Returns:
        - id: unique file ID
        - original: URL to original file
        - optimized: URL to WebP version
        - thumbnail: URL to thumbnail
    """
    try:
        result = await upload_image(file, category)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.delete("/{file_id}")
async def delete_media(
    file_id: str,
    category: str = Query(default="blog", description="Category: blog, icons, etc.")
):
    """
    Delete image and all its variants
    """
    deleted = delete_image(file_id, category)
    if not deleted:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"status": "deleted", "id": file_id}
