import logging
import tempfile
import aiofiles

from fastapi import APIRouter, UploadFile, HTTPException, status

from storeapi.libs.s3 import s3_upload_file

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024


@router.post("/upload", status_code=201)
async def upload_file(file: UploadFile):
    try:
        with tempfile.NamedTemporaryFile() as temp_file:
            filename = temp_file.name
            logger.info(f"Saving uploaded file temporarily to {filename}")
            async with aiofiles.open(filename, "wb") as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)

            logger.debug(f"Uploading {filename} to S3 as {file.filename}")
            file_url = s3_upload_file(filename, file.filename)
    except Exception as e:
        logger.exception(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There was an error uploading the file",
        )
    return {"detail": f"Successfully uploaded {file.filename}", "file_url": file_url}
