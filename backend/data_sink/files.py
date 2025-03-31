# backend/data_sink/files.py

import os
import sys
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from backend.data_sink.auth import get_current_user
from backend.data_source.models import FileInfo, DirectoryContents, DATA_DIR

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from backend.common.logging_utils import setup_logger

logger = setup_logger("data_sink.files")

router = APIRouter(prefix="/received")

RECEIVED_DIR = os.path.join(DATA_DIR, "Received Files")
os.makedirs(RECEIVED_DIR, exist_ok=True)
logger.debug(f"File directory received: {RECEIVED_DIR}")

@router.get("/", response_model=DirectoryContents)
def list_received_files(user: str = Depends(get_current_user)):
    logger.debug(f"Request file list (User: {user})")

    if not os.path.isdir(RECEIVED_DIR):
        logger.error(f"Received files directory not found: {RECEIVED_DIR}")
        raise HTTPException(status_code=500, detail="Received files directory not found")

    try:
        files = []
        for entry in os.scandir(RECEIVED_DIR):
            if entry.is_file():
                file_size = os.path.getsize(entry.path)
                files.append(FileInfo(name=entry.name, size=file_size))

        logger.info(f"Successfully listed received file : {len(files)} files")
        return {"path": "received", "directories": [], "files": files}
    except Exception as e:
        logger.error(f"Error occurred during list received files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list received files: {str(e)}")

@router.get("/download")
def download_received_file(name: str, user: str = Depends(get_current_user)):
    logger.debug(f"Request to download received file: '{name}' (User: {user})")

    file_path = os.path.join(RECEIVED_DIR, name)
    if not os.path.isfile(file_path):
        logger.warning(f"Error : Tried to download not-exist file: {name}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_size = os.path.getsize(file_path)
        logger.info(f"Started to download received file: '{name}' ({file_size} bytes)")
        return FileResponse(file_path, filename=name)
    except Exception as e:
        logger.error(f"Error occured during download received file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")