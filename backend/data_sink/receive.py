# backend/data_sink/receive.py

import os
import sys
from fastapi import APIRouter, UploadFile, File, Header, HTTPException

# common 모듈을 사용할 수 있도록 경로 조정
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# 로거 설정
from backend.common.logging_utils import setup_logger

logger = setup_logger("data_sink.receive")

from backend.data_sink.files import RECEIVED_DIR

router = APIRouter()

# Optional: If we expect a header token from Sovity for security
EXPECTED_TOKEN = "SOVITY_SECRET_TOKEN"


@router.post("/receive-file")
async def receive_file(file: UploadFile = File(...), token: str = Header(None)):
    """Endpoint to receive a file from the data connector (Sovity EDC-CE)."""
    logger.info(f"File receive request received: {file.filename}")

    # Simple security check (if token required)
    if EXPECTED_TOKEN and token != EXPECTED_TOKEN:
        logger.warning(f"Unauthorized file receive attempt with invalid token")
        raise HTTPException(status_code=401, detail="Unauthorized sender")

    filename = file.filename
    if not filename:
        logger.warning("File receive request with no filename")
        raise HTTPException(status_code=400, detail="No file provided")

    save_path = os.path.join(RECEIVED_DIR, filename)

    # Check if file already exists
    if os.path.exists(save_path):
        logger.warning(f"File already exists: {filename}")
        # 여기서 덮어쓸지, 오류를 반환할지, 또는 이름을 변경할지를 결정할 수 있습니다.
        # 이 예시에서는 덮어쓰는 방식을 사용합니다.
        logger.info(f"Existing file will be overwritten: {filename}")

    try:
        # Save the incoming file to the received directory
        with open(save_path, "wb") as out_file:
            content = await file.read()
            out_file.write(content)

        file_size = os.path.getsize(save_path)
        logger.info(f"File '{filename}' received successfully. Size: {file_size} bytes")

        return {"msg": f"File '{filename}' received successfully."}
    except Exception as e:
        logger.error(f"Error saving received file '{filename}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")