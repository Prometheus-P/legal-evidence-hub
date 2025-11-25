"""
Authentication API endpoints
POST /auth/login - User login with JWT token issuance
POST /auth/signup - User signup with JWT token issuance
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.schemas import LoginRequest, SignupRequest, TokenResponse
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


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    User signup endpoint

    **Request Body:**
    - email: User's email address
    - password: User's password (min 8 characters)
    - name: User's name
    - accept_terms: Terms acceptance flag (must be true)

    **Response:**
    - access_token: JWT access token
    - token_type: "bearer"
    - expires_in: Token expiration time in seconds
    - user: User information (id, email, name, role, status, created_at)

    **Errors:**
    - 400: accept_terms is not true
    - 409: Email already exists

    **Default Role:**
    - All signups are assigned LAWYER role by default

    **Security:**
    - Passwords are hashed with bcrypt before storage
    - JWT tokens are signed with HS256 algorithm
    - Token expiration is configurable via JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    """
    auth_service = AuthService(db)
    return auth_service.signup(
        email=request.email,
        password=request.password,
        name=request.name,
        accept_terms=request.accept_terms
    )
