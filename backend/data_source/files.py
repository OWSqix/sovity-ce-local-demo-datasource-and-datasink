# backend/data_source/files.py

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import os
import shutil
from backend.data_source.models import DirectoryContents, FileInfo, DATA_DIR
from backend.data_source.auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/files")

# Ensure base data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def safe_path(subpath: str) -> str:
    """Resolve subpath within DATA_DIR to prevent directory traversal."""
    base = os.path.abspath(DATA_DIR)
    full_path = os.path.abspath(os.path.join(base, subpath))
    if not full_path.startswith(base):
        # Prevent paths that go outside the base directory
        raise HTTPException(status_code=400, detail="Invalid path")
    return full_path

@router.get("/", response_model=DirectoryContents)
def list_directory(dir: Optional[str] = None, user: str = Depends(get_current_user)):
    """List contents of a directory (defaults to root './data')."""
    target_dir = safe_path(dir) if dir else DATA_DIR
    if not os.path.isdir(target_dir):
        raise HTTPException(status_code=404, detail="Directory not found")
    # List directories and files
    dirs = []
    files = []
    for entry in os.scandir(target_dir):
        if entry.is_dir():
            dirs.append(entry.name)
        else:
            files.append(FileInfo(name=entry.name, size=os.path.getsize(entry.path)))
    return {"path": dir or "", "directories": sorted(dirs), "files": files}

@router.post("/", dependencies=[Depends(get_current_user)])
def upload_file(dir: Optional[str] = Form(None), file: UploadFile = File(...)):
    """Upload a file to the specified directory (or root if not specified)."""
    upload_dir = safe_path(dir) if dir else DATA_DIR
    if not os.path.isdir(upload_dir):
        # Create the directory if it doesn't exist (including any necessary parents)
        os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    # Save the uploaded file to disk
    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)
    return {"msg": f"Uploaded {file.filename} to {dir or '/'}"}

@router.post("/mkdir", dependencies=[Depends(get_current_user)])
def create_directory(path: str):
    """Create a new directory under the given path (relative to DATA_DIR)."""
    new_dir_path = safe_path(path)
    if os.path.exists(new_dir_path):
        raise HTTPException(status_code=400, detail="Path already exists")
    os.makedirs(new_dir_path, exist_ok=False)
    return {"msg": f"Directory '{path}' created."}

@router.delete("/", dependencies=[Depends(get_current_user)])
def delete_item(path: str):
    """Delete a file or an empty directory given its path relative to DATA_DIR."""
    target_path = safe_path(path)
    if os.path.isdir(target_path):
        # Only delete if directory is empty
        if os.listdir(target_path):
            raise HTTPException(status_code=400, detail="Directory is not empty")
        os.rmdir(target_path)
        return {"msg": f"Directory '{path}' deleted."}
    elif os.path.isfile(target_path):
        os.remove(target_path)
        return {"msg": f"File '{path}' deleted."}
    else:
        raise HTTPException(status_code=404, detail="File or directory not found")

@router.get("/download")
def download_file(path: str, user: str = Depends(get_current_user)):
    """Download a file by path. Returns the file content as attachment."""
    file_path = safe_path(path)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    # Use Starlette FileResponse to send file
    from fastapi.responses import FileResponse
    return FileResponse(file_path, filename=os.path.basename(file_path))
