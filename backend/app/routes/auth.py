"""Authentication routes."""
import hashlib
import uuid
import os
from fastapi import APIRouter, HTTPException, Response, Request
from app.models import LoginRequest, LoginResponse, VerifyResponse
from app.db import get_user_by_username, create_user, user_exists
import jwt
from datetime import datetime, timedelta

router = APIRouter()

# Get credentials from environment variables, with MVP defaults
VALID_USERNAME = os.getenv("VALID_USERNAME", "user")
VALID_PASSWORD = os.getenv("VALID_PASSWORD", "password")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash password with SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password."""
    return hash_password(password) == password_hash


def create_jwt_token(user_id: str, username: str) -> str:
    """Create JWT token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/auth/login")
async def login(request: LoginRequest, response: Response):
    """Login endpoint."""
    # MVP: Accept only hardcoded credentials
    if request.username != VALID_USERNAME or request.password != VALID_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if user exists in database
    user = get_user_by_username(VALID_USERNAME)

    if not user:
        # Create user on first login
        user_id = f"user-{uuid.uuid4()}"
        password_hash = hash_password(VALID_PASSWORD)
        create_user(user_id, VALID_USERNAME, password_hash)
    else:
        user_id = user["id"]

    # Create token
    token = create_jwt_token(user_id, VALID_USERNAME)

    # Set cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400,  # 24 hours
    )

    return LoginResponse(
        userId=user_id,
        username=VALID_USERNAME,
        token=token,
        expiresIn=86400,
    )


@router.post("/auth/logout")
async def logout(response: Response):
    """Logout endpoint."""
    response.delete_cookie(key="auth_token")
    return {"message": "Logged out successfully"}


@router.get("/auth/verify")
async def verify(request: Request):
    """Verify token endpoint."""
    # Get token from cookie or header
    token = request.cookies.get("auth_token")
    if not token and "authorization" in request.headers:
        auth_header = request.headers["authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=401, detail="Missing authentication token"
        )

    payload = verify_jwt_token(token)

    return VerifyResponse(
        userId=payload["user_id"],
        username=payload["username"],
        isAuthenticated=True,
    )
