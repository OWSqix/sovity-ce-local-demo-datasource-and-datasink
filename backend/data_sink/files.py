# backend/data_sink/files.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os
from backend.data_source.auth import get_current_user  # reuse the auth dependency & JWT settings from data_source
from backend.data_source.models import FileInfo, DirectoryContents, DATA_DIR

router = APIRouter(prefix="/received")

# Directory to store received files
RECEIVED_DIR = os.path.join(DATA_DIR, "received")
os.makedirs(RECEIVED_DIR, exist_ok=True)

@router.get("/", response_model=DirectoryContents)
def list_received_files(user: str = Depends(get_current_user)):
    """List all files received via the connector (flat list in 'received' dir)."""
    if not os.path.isdir(RECEIVED_DIR):
        raise HTTPException(status_code=500, detail="Received files directory not found")
    files = []
    for entry in os.scandir(RECEIVED_DIR):
        if entry.is_file():
            files.append(FileInfo(name=entry.name, size=os.path.getsize(entry.path)))
    # Return as DirectoryContents for consistency (no subdirectories here)
    return {"path": "received", "directories": [], "files": files}

@router.get("/download")
def download_received_file(name: str, user: str = Depends(get_current_user)):
    """Download a received file by name."""
    file_path = os.path.join(RECEIVED_DIR, name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=name)
