# backend/data_sink/receive.py

from fastapi import APIRouter, UploadFile, File, Header, HTTPException
import os
from backend.data_sink.files import RECEIVED_DIR

router = APIRouter()

# Optional: If we expect a header token from Sovity for security
EXPECTED_TOKEN = "SOVITY_SECRET_TOKEN"

@router.post("/receive-file")
async def receive_file(file: UploadFile = File(...), token: str = Header(None)):
    """Endpoint to receive a file from the data connector (Sovity EDC-CE)."""
    # Simple security check (if token required)
    if EXPECTED_TOKEN and token != EXPECTED_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized sender")
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No file provided")
    save_path = os.path.join(RECEIVED_DIR, filename)
    # Save the incoming file to the received directory
    with open(save_path, "wb") as out_file:
        content = await file.read()
        out_file.write(content)
    return {"msg": f"File '{filename}' received successfully."}
