# backend/data_sink/files.py

import os
import sys
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from backend.data_sink.auth import get_current_user
from backend.data_source.models import FileInfo, DirectoryContents, DATA_DIR

# common 모듈을 사용할 수 있도록 경로 조정
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# 로거 설정
from backend.common.logging_utils import setup_logger

logger = setup_logger("data_sink.files")

router = APIRouter(prefix="/received")

# 수신된 파일 저장 디렉토리
RECEIVED_DIR = os.path.join(DATA_DIR, "Received Files")
os.makedirs(RECEIVED_DIR, exist_ok=True)
logger.debug(f"수신 파일 디렉토리 확인: {RECEIVED_DIR}")


@router.get("/", response_model=DirectoryContents)
def list_received_files(user: str = Depends(get_current_user)):
    """커넥터를 통해 수신된 모든 파일 목록 ('received' 디렉토리의 평면 목록)."""
    logger.debug(f"수신 파일 목록 요청 (사용자: {user})")

    if not os.path.isdir(RECEIVED_DIR):
        logger.error(f"수신 파일 디렉토리를 찾을 수 없음: {RECEIVED_DIR}")
        raise HTTPException(status_code=500, detail="Received files directory not found")

    try:
        files = []
        for entry in os.scandir(RECEIVED_DIR):
            if entry.is_file():
                file_size = os.path.getsize(entry.path)
                files.append(FileInfo(name=entry.name, size=file_size))

        logger.info(f"수신 파일 목록 조회 완료: {len(files)} 파일")
        # 일관성을 위해 DirectoryContents로 반환 (여기서는 하위 디렉토리 없음)
        return {"path": "received", "directories": [], "files": files}
    except Exception as e:
        logger.error(f"수신 파일 목록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list received files: {str(e)}")


@router.get("/download")
def download_received_file(name: str, user: str = Depends(get_current_user)):
    """이름으로 수신된 파일 다운로드."""
    logger.debug(f"수신 파일 다운로드 요청: '{name}' (사용자: {user})")

    file_path = os.path.join(RECEIVED_DIR, name)
    if not os.path.isfile(file_path):
        logger.warning(f"존재하지 않는 수신 파일 다운로드 시도: {name}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_size = os.path.getsize(file_path)
        logger.info(f"수신 파일 다운로드 시작: '{name}' ({file_size} 바이트)")
        return FileResponse(file_path, filename=name)
    except Exception as e:
        logger.error(f"수신 파일 다운로드 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")