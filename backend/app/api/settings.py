"""
Settings API Router
006-settings-backend Implementation

API endpoints for user settings management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.schemas import (
    ProfileSettingsUpdate,
    NotificationSettingsUpdate,
    PrivacySettingsUpdate,
    SecuritySettingsUpdate,
    ProfileSettingsOut,
    NotificationSettingsOut,
    SecuritySettingsOut,
    UserSettingsResponse,
)
from app.core.dependencies import get_current_user_id
from app.services.settings_service import SettingsService
from app.services.audit_service import AuditService


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=UserSettingsResponse)
async def get_settings(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get all user settings.

    Returns profile, notification, and security settings.
    """
    service = SettingsService(db)
    settings = service.get_settings(user_id)

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return settings


@router.get("/profile", response_model=ProfileSettingsOut)
async def get_profile_settings(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get profile settings.

    Returns display name, avatar, timezone, and language.
    """
    service = SettingsService(db)
    settings = service.get_profile_settings(user_id)

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return settings


@router.put("/profile", response_model=ProfileSettingsOut)
async def update_profile_settings(
    data: ProfileSettingsUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update profile settings.

    Updatable fields:
    - display_name: Display name (max 100 chars)
    - avatar_url: Avatar image URL
    - timezone: Timezone string (e.g., "Asia/Seoul")
    - language: Language code (e.g., "ko", "en")
    """
    service = SettingsService(db)
    settings = service.update_profile_settings(user_id, data)

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Audit logging
    audit_service = AuditService(db)
    audit_service.log(
        user_id=user_id,
        action="update_profile_settings",
        resource_type="settings",
        resource_id=user_id,
        details=data.model_dump(exclude_none=True),
    )

    return settings


@router.get("/notifications", response_model=NotificationSettingsOut)
async def get_notification_settings(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get notification settings.

    Returns email, push, and frequency preferences.
    """
    service = SettingsService(db)
    settings = service.get_notification_settings(user_id)

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return settings


@router.put("/notifications", response_model=NotificationSettingsOut)
async def update_notification_settings(
    data: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update notification settings.

    Updatable fields:
    - email_notifications: Enable/disable email notifications
    - push_notifications: Enable/disable push notifications
    - notification_frequency: immediate, daily, or weekly
    """
    service = SettingsService(db)
    settings = service.update_notification_settings(user_id, data)

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Audit logging
    audit_service = AuditService(db)
    audit_service.log(
        user_id=user_id,
        action="update_notification_settings",
        resource_type="settings",
        resource_id=user_id,
        details=data.model_dump(exclude_none=True),
    )

    return settings


@router.put("/privacy")
async def update_privacy_settings(
    data: PrivacySettingsUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update privacy settings.

    Updatable fields:
    - profile_visibility: public, team, or private
    """
    service = SettingsService(db)
    success = service.update_privacy_settings(user_id, data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Audit logging
    audit_service = AuditService(db)
    audit_service.log(
        user_id=user_id,
        action="update_privacy_settings",
        resource_type="settings",
        resource_id=user_id,
        details=data.model_dump(exclude_none=True),
    )

    return {"message": "Privacy settings updated"}


@router.get("/security", response_model=SecuritySettingsOut)
async def get_security_settings(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get security settings.

    Returns 2FA status and last password change date.
    """
    service = SettingsService(db)
    settings = service.get_security_settings(user_id)

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return settings


@router.put("/security", response_model=SecuritySettingsOut)
async def update_security_settings(
    data: SecuritySettingsUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update security settings.

    Updatable fields:
    - two_factor_enabled: Enable/disable 2FA
    """
    service = SettingsService(db)
    settings = service.update_security_settings(user_id, data)

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Audit logging
    audit_service = AuditService(db)
    audit_service.log(
        user_id=user_id,
        action="update_security_settings",
        resource_type="settings",
        resource_id=user_id,
        details=data.model_dump(exclude_none=True),
    )

    return settings
