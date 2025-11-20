"""
FastAPI dependencies for authentication and authorization
"""

from fastapi import Depends, Header
from typing import Optional
from app.core.security import decode_access_token
from app.middleware import AuthenticationError


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract and validate user ID from JWT token

    Args:
        authorization: Authorization header (Bearer token)

    Returns:
        User ID from token

    Raises:
        AuthenticationError: Invalid or missing token
    """
    if not authorization:
        raise AuthenticationError("인증이 필요합니다.")

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("잘못된 인증 형식입니다.")

    token = parts[1]

    # Decode and validate token
    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationError("유효하지 않은 토큰입니다.")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("토큰에 사용자 정보가 없습니다.")

    return user_id
