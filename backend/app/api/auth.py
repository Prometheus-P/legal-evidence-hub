"""
Authentication API endpoints
POST /auth/login - User login with JWT token issuance
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.schemas import LoginRequest, TokenResponse
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login endpoint

    **Request Body:**
    - email: User's email address
    - password: User's password

    **Response:**
    - access_token: JWT access token
    - token_type: "bearer"
    - expires_in: Token expiration time in seconds
    - user: User information (id, email, name, role)

    **Errors:**
    - 401: Authentication failed (invalid email or password)

    **Security:**
    - Error messages are intentionally generic to prevent user enumeration
    - JWT tokens are signed with HS256 algorithm
    - Token expiration is configurable via JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    """
    auth_service = AuthService(db)
    return auth_service.login(credentials.email, credentials.password)
