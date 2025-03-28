# backend/data_sink/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.data_sink import files as files_router
from backend.data_sink import receive as receive_router

app = FastAPI(title="Data Sink API")

# CORS (allow Angular app to call listing/download endpoints)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure received files directory exists
RECEIVED_DIR = os.path.join("./data", "received")
os.makedirs(RECEIVED_DIR, exist_ok=True)

# Include routers
app.include_router(receive_router.router)
app.include_router(files_router.router)
