# backend/data_source/auth.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
import jwt  # PyJWT
from backend.data_source.models import UserCreate, UserLogin

router = APIRouter(prefix="/auth")

# In-memory user store: {username: password_hash}
users_db = {}

# Secret key for JWT (in practice, keep this safe and unique)
SECRET_KEY = "SUPER_SECRET_JWT_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Dependency to get current user from token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Verify JWT and return username of the logged-in user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return username

@router.post("/register", status_code=201)
def register_user(user: UserCreate):
    """Register a new user with username and password."""
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    # For simplicity, store password in plain (DO NOT do this in real systems)
    # Ideally, use bcrypt to hash the password.
    users_db[user.username] = user.password
    return {"msg": f"User '{user.username}' registered successfully."}

@router.post("/login")
def login(user: UserLogin):
    """Authenticate user and return JWT token."""
    # Validate credentials
    stored_pwd = users_db.get(user.username)
    if stored_pwd is None or stored_pwd != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Create JWT token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.username, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "token_type": "bearer"}
