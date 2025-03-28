# backend/data_source/files.py

import os
import sys
import shutil
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from backend.data_source.models import DirectoryContents, FileInfo, DATA_DIR, DirectoryRequest
from backend.data_source.auth import get_current_user
from typing import Optional

# common 모듈을 사용할 수 있도록 경로 조정
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# 로거 설정
from backend.common.logging_utils import setup_logger

logger = setup_logger("data_source.files")

router = APIRouter(prefix="/files")

# 기본 데이터 디렉토리 확인
os.makedirs(DATA_DIR, exist_ok=True)
logger.debug(f"기본 데이터 디렉토리 확인: {DATA_DIR}")


def safe_path(subpath: str) -> str:
    """경로 주입 공격 방지를 위한 안전한 경로 해석."""
    base = os.path.abspath(DATA_DIR)
    full_path = os.path.abspath(os.path.join(base, subpath))
    if not full_path.startswith(base):
        logger.warning(f"디렉토리 탐색 시도 감지: {subpath}")
        # 기본 디렉토리 외부 경로 방지
        raise HTTPException(status_code=400, detail="Invalid path")
    return full_path


@router.get("/", response_model=DirectoryContents)
def list_directory(dir: Optional[str] = None, user: str = Depends(get_current_user)):
    """디렉토리 내용 조회 (기본값: 루트 './data')."""
    logger.debug(f"디렉토리 조회 요청: '{dir or 'root'}' (사용자: {user})")

    target_dir = safe_path(dir) if dir else DATA_DIR
    if not os.path.isdir(target_dir):
        logger.warning(f"존재하지 않는 디렉토리 요청: {dir}")
        raise HTTPException(status_code=404, detail="Directory not found")

    # 디렉토리 및 파일 목록 작성
    dirs = []
    files = []
    try:
        for entry in os.scandir(target_dir):
            if entry.is_dir():
                dirs.append(entry.name)
            else:
                files.append(FileInfo(name=entry.name, size=os.path.getsize(entry.path)))

        logger.info(f"디렉토리 '{dir or 'root'}' 조회 완료: {len(dirs)} 디렉토리, {len(files)} 파일")
        return {"path": dir or "", "directories": sorted(dirs), "files": files}
    except Exception as e:
        logger.error(f"디렉토리 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list directory: {str(e)}")


@router.post("/", dependencies=[Depends(get_current_user)])
def upload_file(dir: Optional[str] = Form(None), file: UploadFile = File(...), user: str = Depends(get_current_user)):
    """파일 업로드 (지정된 디렉토리 또는 루트)."""
    logger.debug(f"파일 업로드 요청: '{file.filename}' -> '{dir or 'root'}' (사용자: {user})")

    upload_dir = safe_path(dir) if dir else DATA_DIR
    if not os.path.isdir(upload_dir):
        logger.info(f"업로드 디렉토리 생성: {dir}")
        # 디렉토리가 없으면 생성 (필요한 부모 디렉토리 포함)
        os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    try:
        # 업로드된 파일을 디스크에 저장
        with open(file_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)

        file_size = os.path.getsize(file_path)
        logger.info(f"파일 업로드 완료: '{file.filename}' ({file_size} 바이트) -> '{dir or '/'}'")
        return {"msg": f"Uploaded {file.filename} to {dir or '/'}"}
    except Exception as e:
        logger.error(f"파일 업로드 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/mkdir", dependencies=[Depends(get_current_user)])
def create_directory(request: DirectoryRequest, user: str = Depends(get_current_user)):
    """새 디렉토리 생성 (DATA_DIR 하위 상대 경로)."""
    path = request.path
    logger.debug(f"디렉토리 생성 요청: '{path}' (사용자: {user})")

    new_dir_path = safe_path(path)
    if os.path.exists(new_dir_path):
        logger.warning(f"이미 존재하는 경로에 디렉토리 생성 시도: {path}")
        raise HTTPException(status_code=400, detail="Path already exists")

    try:
        os.makedirs(new_dir_path, exist_ok=False)
        logger.info(f"디렉토리 생성 완료: '{path}'")
        return {"msg": f"Directory '{path}' created."}
    except Exception as e:
        logger.error(f"디렉토리 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}")


@router.delete("/", dependencies=[Depends(get_current_user)])
def delete_item(path: str, user: str = Depends(get_current_user)):
    """파일 또는 빈 디렉토리 삭제 (DATA_DIR 하위 상대 경로)."""
    logger.debug(f"삭제 요청: '{path}' (사용자: {user})")

    target_path = safe_path(path)
    try:
        if os.path.isdir(target_path):
            # 디렉토리가 비어있는 경우에만 삭제
            if os.listdir(target_path):
                logger.warning(f"비어있지 않은 디렉토리 삭제 시도: {path}")
                raise HTTPException(status_code=400, detail="Directory is not empty")
            os.rmdir(target_path)
            logger.info(f"디렉토리 삭제 완료: '{path}'")
            return {"msg": f"Directory '{path}' deleted."}
        elif os.path.isfile(target_path):
            os.remove(target_path)
            logger.info(f"파일 삭제 완료: '{path}'")
            return {"msg": f"File '{path}' deleted."}
        else:
            logger.warning(f"존재하지 않는 항목 삭제 시도: {path}")
            raise HTTPException(status_code=404, detail="File or directory not found")
    except HTTPException:
        # 기존 HTTP 예외는 그대로 전달
        raise
    except Exception as e:
        logger.error(f"항목 삭제 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete item: {str(e)}")


@router.get("/download")
def download_file(path: str, user: str = Depends(get_current_user)):
    """파일 다운로드 (경로로 지정). 첨부 파일로 파일 내용을 반환합니다."""
    logger.debug(f"파일 다운로드 요청: '{path}' (사용자: {user})")

    file_path = safe_path(path)
    if not os.path.isfile(file_path):
        logger.warning(f"존재하지 않는 파일 다운로드 시도: {path}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Starlette FileResponse를 사용하여 파일 전송
        from fastapi.responses import FileResponse
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        logger.info(f"파일 다운로드 시작: '{filename}' ({file_size} 바이트)")
        return FileResponse(file_path, filename=filename)
    except Exception as e:
        logger.error(f"파일 다운로드 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")