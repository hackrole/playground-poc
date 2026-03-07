import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from playground.clients.s3_client import StorageError, get_s3_client
from playground.constants import S3_UPLOAD_FOLDER

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    """Upload a CSV file to S3 storage.

    Args:
        file: CSV file to upload.

    Returns:
        Dictionary containing signed_url to access the uploaded file.

    Raises:
        HTTPException: If upload fails.
    """
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(status_code=400, detail="Invalid file upload")

    file_hash = get_s3_client().compute_file_hash(content)
    key = f"{S3_UPLOAD_FOLDER}/{file_hash}.csv"

    try:
        get_s3_client().upload_csv(content, key)
    except StorageError as e:
        logger.error(f"Failed to upload file to S3: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

    try:
        signed_url = get_s3_client().generate_signed_url(key)
    except StorageError as e:
        logger.error(f"Failed to generate signed URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate signed URL")

    return {"signed_url": signed_url}
