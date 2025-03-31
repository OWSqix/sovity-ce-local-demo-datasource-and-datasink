# backend/data_sink/main.py

import os
import logging.config
import sys

from backend.data_sink import files as files_router
from backend.data_sink import receive as receive_router
from backend.data_source.auth import router as auth_router

from fastapi import FastAPI, Request

from fastapi.middleware.cors import CORSMiddleware
from backend.common.logging_utils import setup_logger, LogConfig
from backend.common.cli_parser import get_service_settings

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

settings = get_service_settings("data_sink")

logger = setup_logger(
    "data_sink",
    level=settings.get("log_level"),
    log_file=settings.get("log_file"),
    detailed_format=settings.get("detailed_logs", False)
)

logging_config = LogConfig.get_config(
    "data_sink",
    log_level=settings.get("log_level"),
    log_file=settings.get("log_file")
)
logging.config.dictConfig(logging_config)

app = FastAPI(title="Data Sink API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Local development for provider frontend
        "http://localhost:4201",  # Local development for consumer frontend
        "http://host.docker.internal:4200",  # Docker internal access for provider frontend
        "http://host.docker.internal:4201",  # Docker internal access for consumer frontend
        "http://provider-frontend:4200",  # Docker service name for provider frontend
        "http://consumer-frontend:4200",  # Docker service name for consumer frontend (internal port)
        "http://provider:11000",  # Caddy proxy for provider
        "http://consumer:22000",  # Caddy proxy for consumer
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Data Sink API service started.")
    logger.info(f"Host: {settings.get('host')}, Port: {settings.get('port')}")
    logger.info(f"Log level: {settings.get('log_level')}")

    received_dir = os.path.join("./data", "received")
    if not os.path.isdir(received_dir):
        os.makedirs(received_dir, exist_ok=True)
        logger.info(f"File directory generated: {received_dir}")
    else:
        logger.debug(f"File directory check: {received_dir}")

    my_files_dir = os.path.join("./data", "uploaded")
    if not os.path.isdir(my_files_dir):
        os.makedirs(my_files_dir, exist_ok=True)
        logger.info(f"File directory generated: {my_files_dir}")
    else:
        logger.debug(f"File directory check: {my_files_dir}")

app.include_router(receive_router.router)
app.include_router(files_router.router)
app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Data Sink API service started with uvicorn...")
    uvicorn.run(
        "backend.data_sink.main:app",
        host="0.0.0.0",
        port=settings.get("port"),
        reload=True,
        log_level=settings.get("log_level")
    )