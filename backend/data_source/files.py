import os
import sys
import shutil
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from backend.data_source.models import DirectoryContents, FileInfo, DATA_DIR, DirectoryRequest
from backend.data_source.auth import get_current_user
from typing import Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from backend.common.logging_utils import setup_logger

logger = setup_logger("data_source.files")

router = APIRouter(prefix="/files")

os.makedirs(DATA_DIR, exist_ok=True)
logger.debug(f"Checking base data directory: {DATA_DIR}")


def safe_path(subpath: str) -> str:
    base = os.path.abspath(DATA_DIR)
    full_path = os.path.abspath(os.path.join(base, subpath))
    if not full_path.startswith(base):
        logger.warning(f"Directory traversal attempt detected: {subpath}")
        raise HTTPException(status_code=400, detail="Invalid path")
    return full_path


@router.get("/", response_model=DirectoryContents)
def list_directory(dir: Optional[str] = None, user: str = Depends(get_current_user)):
    logger.debug(f"Directory listing request: '{dir or 'root'}' (user: {user})")

    target_dir = safe_path(dir) if dir else DATA_DIR
    if not os.path.isdir(target_dir):
        logger.warning(f"Request for non-existent directory: {dir}")
        raise HTTPException(status_code=404, detail="Directory not found")

    dirs = []
    files = []
    try:
        for entry in os.scandir(target_dir):
            if entry.is_dir():
                dirs.append(entry.name)
            else:
                files.append(FileInfo(name=entry.name, size=os.path.getsize(entry.path)))

        logger.info(f"Directory '{dir or 'root'}' listing complete: {len(dirs)} directories, {len(files)} files")
        return {"path": dir or "", "directories": sorted(dirs), "files": files}
    except Exception as e:
        logger.error(f"Error occurred while listing directory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list directory: {str(e)}")


@router.post("/", dependencies=[Depends(get_current_user)])
def upload_file(dir: Optional[str] = Form(None), file: UploadFile = File(...), user: str = Depends(get_current_user)):
    logger.debug(f"File upload request: '{file.filename}' -> '{dir or 'root'}' (user: {user})")

    upload_dir = safe_path(dir) if dir else DATA_DIR
    if not os.path.isdir(upload_dir):
        logger.info(f"Creating upload directory: {dir}")
        os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    try:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted existing file for overwrite: {file_path}")
                import time
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error occurred while deleting existing file: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to replace existing file: {str(e)}")

        with open(file_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)

        file_size = os.path.getsize(file_path)
        logger.info(f"File upload complete: '{file.filename}' ({file_size} bytes) -> '{dir or '/'}'")
        return {"msg": f"Uploaded {file.filename} to {dir or '/'}"}
    except Exception as e:
        logger.error(f"Error occurred during file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/mkdir", dependencies=[Depends(get_current_user)])
def create_directory(request: DirectoryRequest, user: str = Depends(get_current_user)):
    path = request.path
    logger.debug(f"Directory creation request: '{path}' (user: {user})")

    new_dir_path = safe_path(path)
    if os.path.exists(new_dir_path):
        logger.warning(f"Attempt to create directory at existing path: {path}")
        raise HTTPException(status_code=400, detail="Path already exists")

    try:
        os.makedirs(new_dir_path, exist_ok=False)
        logger.info(f"Directory creation complete: '{path}'")
        return {"msg": f"Directory '{path}' created."}
    except Exception as e:
        logger.error(f"Error occurred during directory creation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}")


@router.delete("/", dependencies=[Depends(get_current_user)])
def delete_item(path: str, user: str = Depends(get_current_user)):
    logger.debug(f"Deletion request: '{path}' (user: {user})")

    target_path = safe_path(path)
    try:
        if os.path.isdir(target_path):
            if os.listdir(target_path):
                logger.warning(f"Attempt to delete non-empty directory: {path}")
                raise HTTPException(status_code=400, detail="Directory is not empty")
            os.rmdir(target_path)
            logger.info(f"Directory deletion complete: '{path}'")
            return {"msg": f"Directory '{path}' deleted."}
        elif os.path.isfile(target_path):
            os.remove(target_path)
            logger.info(f"File deletion complete: '{path}'")
            return {"msg": f"File '{path}' deleted."}
        else:
            logger.warning(f"Attempt to delete non-existent item: {path}")
            raise HTTPException(status_code=404, detail="File or directory not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error occurred during item deletion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete item: {str(e)}")


@router.get("/download")
def download_file(path: str, user: str = Depends(get_current_user)):
    logger.debug(f"File download request: '{path}' (user: {user})")

    file_path = safe_path(path)
    if not os.path.isfile(file_path):
        logger.warning(f"Attempt to download non-existent file: {path}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        from fastapi.responses import FileResponse
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        logger.info(f"Starting file download: '{filename}' ({file_size} bytes)")
        return FileResponse(file_path, filename=filename)
    except Exception as e:
        logger.error(f"Error occurred during file download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")