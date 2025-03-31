import os
import logging.config
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.common.logging_utils import setup_logger, LogConfig
from backend.common.cli_parser import get_service_settings

settings = get_service_settings("data_source")

logger = setup_logger(
    "data_source",
    level=settings.get("log_level"),
    log_file=settings.get("log_file"),
    detailed_format=settings.get("detailed_logs", False)
)

logging_config = LogConfig.get_config(
    "data_source",
    log_level=settings.get("log_level"),
    log_file=settings.get("log_file")
)
logging.config.dictConfig(logging_config)

app = FastAPI(title="Data Source API")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:4201",
        "http://host.docker.internal:4200",
        "http://host.docker.internal:4201",
        "http://provider-frontend:4200",
        "http://consumer-frontend:4200",
        "http://provider:11000",
        "http://consumer:22000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.data_source.auth import router as auth_router
from backend.data_source.files import router as files_router

app.include_router(auth_router)
app.include_router(files_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Data Source API service has started.")
    logger.info(f"Host: {settings.get('host')}, Port: {settings.get('port')}")
    logger.info(f"Log level: {settings.get('log_level')}")

    data_dir = "./data"
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Default data directory created: {data_dir}")
    else:
        logger.debug(f"Default data directory confirmed: {data_dir}")


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Running Data Source API service with Uvicorn...")
    uvicorn.run(
        "backend.data_source.main:app",
        host="0.0.0.0",
        port=settings.get("port"),
        reload=True,
        log_level=settings.get("log_level")
    )