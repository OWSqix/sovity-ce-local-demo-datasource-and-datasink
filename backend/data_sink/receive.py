import os
import sys
import uuid
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException, Request
from backend.data_sink.auth import validate_request_auth
from backend.data_sink.files import RECEIVED_DIR
from backend.common.logging_utils import setup_logger

# Set directory path to use common module
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

logger = setup_logger("data_sink.receive")
router = APIRouter()

@router.post("/receive-file")
async def receive_file(
        request: Request,
        authorization: str = Header(default=None)
):

    logger.debug(f"Received authorization token: authorization={authorization}")
    logger.debug(f"All headers: {dict(request.headers)}")

    auth_info = await validate_request_auth(request, authorization)
    logger.info(f"Authentication success: method={auth_info.get('method')}, user={auth_info.get('user')}")

    content_type = request.headers.get("content-type", "application/octet-stream")
    logger.debug(f"Received content-type: {content_type}")

    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="CANNOT FIND ANY FILE DATA")

    # File size limit code(1gb). Activate if you need :)
    # if len(body) > 1024 * 1024 * 1024:
    #     raise HTTPException(status_code=413, detail="FILE IS TOO BIG")

    filename = None
    content_disposition = request.headers.get("content-disposition")
    if content_disposition and "filename=" in content_disposition:
        try:
            filename = content_disposition.split("filename=")[1].strip('"\'')
        except Exception as e:
            logger.warning(f"content-disposition parse failed: {e}")

    # If failed to parse filename then generate unique filename with timestamp and uuid
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]

        extension = "bin"
        if "json" in content_type:
            extension = "json"
        elif "xml" in content_type:
            extension = "xml"
        elif "text" in content_type:
            extension = "txt"

        filename = f"edc_data_{timestamp}_{unique_id}.{extension}"

    save_path = os.path.join(RECEIVED_DIR, filename)
    try:
        os.makedirs(RECEIVED_DIR, exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(body)
        logger.info(f"File saved in: {save_path}")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "msg": "File is successfully transferred",
        "size": len(body),
        "filename": filename,
        "content_type": content_type
    }