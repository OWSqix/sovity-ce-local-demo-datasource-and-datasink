# backend/data_source/models.py

from pydantic import BaseModel

DATA_DIR = "./data"

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class FileInfo(BaseModel):
    name: str
    size: int

class DirectoryContents(BaseModel):
    path: str
    directories: list[str]
    files: list[FileInfo]

class DirectoryRequest(BaseModel):
    path: str