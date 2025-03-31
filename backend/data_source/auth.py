# backend/data_source/auth.py - Improved Version with Password Hashing and Logging

import os
import sys
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from backend.data_source.models import UserCreate, UserLogin

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from backend.common.logging_utils import setup_logger
from backend.common.auth_store import users_db, JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

logger = setup_logger("data_source.auth")

router = APIRouter(prefix="/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", JWT_SECRET_KEY)
ALGORITHM = JWT_ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in users_db:
            logger.warning(f"Invalid username in token or user not found: {username}")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning(f"Token expired for user: {username}")
            raise HTTPException(status_code=401, detail="Token has expired")

        logger.debug(f"Authenticated user: {username}")
        return username
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.post("/register", status_code=201)
def register_user(user: UserCreate):
    logger.info(f"Registration attempt for username: {user.username}")

    if user.username in users_db:
        logger.warning(f"Registration failed: Username already exists: {user.username}")
        raise HTTPException(status_code=400, detail="Username already registered")

    if len(user.password) < 6:
        logger.warning(f"Registration failed: Password too short for user: {user.username}")
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    hashed_password = get_password_hash(user.password)
    users_db[user.username] = hashed_password

    logger.info(f"User registered successfully: {user.username}")
    return {"msg": f"User '{user.username}' registered successfully."}


@router.post("/login")
def login(user: UserLogin):
    logger.info(f"Login attempt for username: {user.username}")

    stored_pwd_hash = users_db.get(user.username)
    if stored_pwd_hash is None:
        logger.warning(f"Login failed: User not found: {user.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(user.password, stored_pwd_hash):
        logger.warning(f"Login failed: Invalid password for user: {user.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.username,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    logger.info(f"User logged in successfully: {user.username}")
    logger.debug(f"Token issued for user: {user.username}, expires in {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")

    return {
        "token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }