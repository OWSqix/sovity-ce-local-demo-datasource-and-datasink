# backend/data_source/auth.py - Improved Version with Password Hashing

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
import jwt  # PyJWT
import os
from passlib.context import CryptContext  # For password hashing
from backend.data_source.models import UserCreate, UserLogin

router = APIRouter(prefix="/auth")

# Password hashing using passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store: {username: hashed_password}
# In production, use a database instead
users_db = {}

# Secret key for JWT - Use environment variables in production
# Generate a secure random key, don't use this example key
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "SUPER_SECRET_JWT_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Dependency to get current user from token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Verify JWT and return username of the logged-in user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        # Check token expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(status_code=401, detail="Token has expired")
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

    # Validate password strength (example, add more rules as needed)
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Hash the password before storing
    hashed_password = get_password_hash(user.password)
    users_db[user.username] = hashed_password

    return {"msg": f"User '{user.username}' registered successfully."}


@router.post("/login")
def login(user: UserLogin):
    """Authenticate user and return JWT token."""
    # Get stored hashed password
    stored_pwd_hash = users_db.get(user.username)
    if stored_pwd_hash is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Verify password
    if not verify_password(user.password, stored_pwd_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT token with expiration
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.username,
        "exp": expire,
        "iat": datetime.utcnow(),  # issued at
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    }