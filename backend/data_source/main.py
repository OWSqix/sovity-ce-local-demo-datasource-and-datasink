# backend/data_source/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.data_source.auth import router as auth_router
from backend.data_source.files import router as files_router

app = FastAPI(title="Data Source API")

# Allow frontend origin for CORS (adjust the origins list as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication and file management routes
app.include_router(auth_router)
app.include_router(files_router)

# Create base data directory on startup if not exists
DATA_DIR = "./data"
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR)
