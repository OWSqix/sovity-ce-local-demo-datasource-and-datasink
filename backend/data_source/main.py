# backend/data_source/main.py

import os
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
settings = get_service_settings("data_source")

# 로거 설정
logger = setup_logger(
    "data_source",
    level=settings.get("log_level"),
    log_file=settings.get("log_file"),
    detailed_format=settings.get("detailed_logs", False)
)

# FastAPI 로깅 설정
logging_config = LogConfig.get_config(
    "data_source",
    log_level=settings.get("log_level"),
    log_file=settings.get("log_file")
)
logging.config.dictConfig(logging_config)

# FastAPI 애플리케이션 생성
app = FastAPI(title="Data Source API")


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
    allow_origins=["http://localhost:4200", "http://host.docker.internal:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 임포트 및 포함
from backend.data_source.auth import router as auth_router
from backend.data_source.files import router as files_router

app.include_router(auth_router)
app.include_router(files_router)


# 시작 이벤트 핸들러 추가
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행됩니다."""
    logger.info("Data Source API 서비스가 시작되었습니다.")
    logger.info(f"호스트: {settings.get('host')}, 포트: {settings.get('port')}")
    logger.info(f"로그 레벨: {settings.get('log_level')}")

    # 기본 데이터 디렉토리 생성
    data_dir = "./data"
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
        logger.info(f"기본 데이터 디렉토리 생성됨: {data_dir}")
    else:
        logger.debug(f"기본 데이터 디렉토리 확인됨: {data_dir}")


# 앱 실행 코드 (직접 실행 시)
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Uvicorn으로 Data Source API 서비스 실행 중...")
    uvicorn.run(
        "backend.data_source.main:app",
        host="0.0.0.0",
        port=settings.get("port"),
        reload=True,
        log_level=settings.get("log_level")
    )