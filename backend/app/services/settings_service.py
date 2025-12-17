"""
Settings Service
006-settings-backend Implementation

Business logic for user settings management.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import User, UserSettings, NotificationFrequency, ProfileVisibility
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


class SettingsService:
    """Service for user settings operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_settings(self, user_id: str) -> Optional[UserSettingsResponse]:
        """
        Get complete user settings.

        Args:
            user_id: ID of the user

        Returns:
            UserSettingsResponse with all settings or None if user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        settings = self._get_or_create_settings(user_id)

        return UserSettingsResponse(
            profile=ProfileSettingsOut(
                display_name=settings.display_name,
                email=user.email,
                name=user.name,
                phone=None,
                avatar_url=settings.avatar_url,
                timezone=settings.timezone,
                language=settings.language,
            ),
            notifications=NotificationSettingsOut(
                email_enabled=settings.email_notifications,
                push_enabled=settings.push_notifications,
                frequency=settings.notification_frequency,
            ),
            security=SecuritySettingsOut(
                two_factor_enabled=settings.two_factor_enabled,
                last_password_change=settings.last_password_change,
            ),
        )

    def get_profile_settings(self, user_id: str) -> Optional[ProfileSettingsOut]:
        """Get only profile settings for a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        settings = self._get_or_create_settings(user_id)

        return ProfileSettingsOut(
            display_name=settings.display_name,
            email=user.email,
            name=user.name,
            phone=None,
            avatar_url=settings.avatar_url,
            timezone=settings.timezone,
            language=settings.language,
        )

    def get_notification_settings(self, user_id: str) -> Optional[NotificationSettingsOut]:
        """Get only notification settings for a user."""
        settings = self._get_or_create_settings(user_id)
        if not settings:
            return None

        return NotificationSettingsOut(
            email_enabled=settings.email_notifications,
            push_enabled=settings.push_notifications,
            frequency=settings.notification_frequency,
        )

    def get_security_settings(self, user_id: str) -> Optional[SecuritySettingsOut]:
        """Get only security settings for a user."""
        settings = self._get_or_create_settings(user_id)
        if not settings:
            return None

        return SecuritySettingsOut(
            two_factor_enabled=settings.two_factor_enabled,
            last_password_change=settings.last_password_change,
        )

    def update_profile_settings(
        self, user_id: str, data: ProfileSettingsUpdate
    ) -> Optional[ProfileSettingsOut]:
        """
        Update profile settings for a user.

        Args:
            user_id: ID of the user
            data: Profile settings to update

        Returns:
            Updated profile settings or None if user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        settings = self._get_or_create_settings(user_id)

        if data.display_name is not None:
            settings.display_name = data.display_name
        if data.avatar_url is not None:
            settings.avatar_url = data.avatar_url
        if data.timezone is not None:
            settings.timezone = data.timezone
        if data.language is not None:
            settings.language = data.language

        self.db.commit()
        self.db.refresh(settings)

        return ProfileSettingsOut(
            display_name=settings.display_name,
            email=user.email,
            name=user.name,
            phone=None,
            avatar_url=settings.avatar_url,
            timezone=settings.timezone,
            language=settings.language,
        )

    def update_notification_settings(
        self, user_id: str, data: NotificationSettingsUpdate
    ) -> Optional[NotificationSettingsOut]:
        """
        Update notification settings for a user.

        Args:
            user_id: ID of the user
            data: Notification settings to update

        Returns:
            Updated notification settings or None if user not found
        """
        settings = self._get_or_create_settings(user_id)
        if not settings:
            return None

        if data.email_notifications is not None:
            settings.email_notifications = data.email_notifications
        if data.push_notifications is not None:
            settings.push_notifications = data.push_notifications
        if data.notification_frequency is not None:
            settings.notification_frequency = data.notification_frequency

        self.db.commit()
        self.db.refresh(settings)

        return NotificationSettingsOut(
            email_enabled=settings.email_notifications,
            push_enabled=settings.push_notifications,
            frequency=settings.notification_frequency,
        )

    def update_privacy_settings(
        self, user_id: str, data: PrivacySettingsUpdate
    ) -> bool:
        """
        Update privacy settings for a user.

        Args:
            user_id: ID of the user
            data: Privacy settings to update

        Returns:
            True if updated, False if user not found
        """
        settings = self._get_or_create_settings(user_id)
        if not settings:
            return False

        if data.profile_visibility is not None:
            settings.profile_visibility = data.profile_visibility

        self.db.commit()
        return True

    def update_security_settings(
        self, user_id: str, data: SecuritySettingsUpdate
    ) -> Optional[SecuritySettingsOut]:
        """
        Update security settings for a user.

        Args:
            user_id: ID of the user
            data: Security settings to update

        Returns:
            Updated security settings or None if user not found
        """
        settings = self._get_or_create_settings(user_id)
        if not settings:
            return None

        if data.two_factor_enabled is not None:
            settings.two_factor_enabled = data.two_factor_enabled

        self.db.commit()
        self.db.refresh(settings)

        return SecuritySettingsOut(
            two_factor_enabled=settings.two_factor_enabled,
            last_password_change=settings.last_password_change,
        )

    def _get_or_create_settings(self, user_id: str) -> Optional[UserSettings]:
        """
        Get existing settings or create default settings for user.

        Args:
            user_id: ID of the user

        Returns:
            UserSettings instance or None if user doesn't exist
        """
        # Check if user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Get existing settings
        settings = (
            self.db.query(UserSettings)
            .filter(UserSettings.user_id == user_id)
            .first()
        )

        # Create default settings if not exists
        if not settings:
            settings = UserSettings(
                user_id=user_id,
                timezone="Asia/Seoul",
                language="ko",
                email_notifications=True,
                push_notifications=True,
                notification_frequency=NotificationFrequency.IMMEDIATE,
                profile_visibility=ProfileVisibility.TEAM,
                two_factor_enabled=False,
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)

        return settings
