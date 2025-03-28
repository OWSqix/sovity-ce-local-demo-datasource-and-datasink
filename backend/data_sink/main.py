# backend/data_sink/main.py

import os
import logging
import logging.config
import sys

# common 모듈을 사용할 수 있도록 경로 조정
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.common.logging_utils import setup_logger, LogConfig
from backend.common.cli_parser import get_service_settings

# 서비스 설정 가져오기
settings = get_service_settings("data_sink")

# 로거 설정
logger = setup_logger(
    "data_sink",
    level=settings.get("log_level"),
    log_file=settings.get("log_file"),
    detailed_format=settings.get("detailed_logs", False)
)

# FastAPI 로깅 설정
logging_config = LogConfig.get_config(
    "data_sink",
    log_level=settings.get("log_level"),
    log_file=settings.get("log_file")
)
logging.config.dictConfig(logging_config)

# FastAPI 애플리케이션 생성
app = FastAPI(title="Data Sink API")


# 로그 미들웨어 추가
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """모든 HTTP 요청을 로깅합니다."""
    logger.debug(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")
    return response


# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 임포트 및 포함
from backend.data_sink import files as files_router
from backend.data_sink import receive as receive_router
from backend.data_source.auth import router as auth_router


# 시작 이벤트 핸들러 추가
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행됩니다."""
    logger.info("Data Sink API 서비스가 시작되었습니다.")
    logger.info(f"호스트: {settings.get('host')}, 포트: {settings.get('port')}")
    logger.info(f"로그 레벨: {settings.get('log_level')}")

    # 수신된 파일 디렉토리 확인
    received_dir = os.path.join("./data", "Received Files")
    if not os.path.isdir(received_dir):
        os.makedirs(received_dir, exist_ok=True)
        logger.info(f"수신된 파일 디렉토리 생성됨: {received_dir}")
    else:
        logger.debug(f"수신된 파일 디렉토리 확인됨: {received_dir}")

    my_files_dir = os.path.join("./data", "My Files")
    if not os.path.isdir(my_files_dir):
        os.makedirs(my_files_dir, exist_ok=True)
        logger.info(f"수신된 파일 디렉토리 생성됨: {my_files_dir}")
    else:
        logger.debug(f"수신된 파일 디렉토리 확인됨: {my_files_dir}")


# 라우터 등록
app.include_router(receive_router.router)
app.include_router(files_router.router)
app.include_router(auth_router)

# 앱 실행 코드 (직접 실행 시)
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Uvicorn으로 Data Sink API 서비스 실행 중...")
    uvicorn.run(
        "backend.data_sink.main:app",
        host=settings.get("host"),
        port=settings.get("port"),
        reload=True,
        log_level=settings.get("log_level")
    )