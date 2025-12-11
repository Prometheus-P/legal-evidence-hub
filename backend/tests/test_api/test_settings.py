"""
Test suite for Settings API endpoints
006-settings-backend Implementation

Tests for:
- GET /settings - Get all user settings
- GET /settings/profile - Get profile settings
- PUT /settings/profile - Update profile settings
- GET /settings/notifications - Get notification settings
- PUT /settings/notifications - Update notification settings
- PUT /settings/privacy - Update privacy settings
- GET /settings/security - Get security settings
- PUT /settings/security - Update security settings
"""

from fastapi import status


class TestGetSettings:
    """Test suite for GET /settings endpoint"""

    def test_should_return_all_settings_for_authenticated_user(
        self, client, auth_headers
    ):
        """
        Given: Authenticated user
        When: GET /settings is called
        Then:
            - Returns 200 status code
            - Response contains profile, notifications, security sections
        """
        # When: GET /settings with auth
        response = client.get("/settings", headers=auth_headers)

        # Then: Success response with all settings
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "profile" in data
        assert "notifications" in data
        assert "security" in data

        # Validate profile structure
        profile = data["profile"]
        assert "email" in profile
        assert "name" in profile
        assert "timezone" in profile
        assert "language" in profile

        # Validate notifications structure
        notifications = data["notifications"]
        assert "email_enabled" in notifications
        assert "push_enabled" in notifications
        assert "frequency" in notifications

        # Validate security structure
        security = data["security"]
        assert "two_factor_enabled" in security

    def test_should_return_401_for_unauthenticated_request(self, client):
        """
        Given: No authentication
        When: GET /settings is called
        Then: Returns 401 Unauthorized
        """
        # When: GET /settings without auth
        response = client.get("/settings")

        # Then: 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetProfileSettings:
    """Test suite for GET /settings/profile endpoint"""

    def test_should_return_profile_settings(self, client, auth_headers, test_user):
        """
        Given: Authenticated user
        When: GET /settings/profile is called
        Then:
            - Returns 200 status code
            - Response contains user email and name
            - Default timezone is Asia/Seoul
            - Default language is ko
        """
        # When: GET /settings/profile
        response = client.get("/settings/profile", headers=auth_headers)

        # Then: Success response
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["timezone"] == "Asia/Seoul"  # Default
        assert data["language"] == "ko"  # Default


class TestUpdateProfileSettings:
    """Test suite for PUT /settings/profile endpoint"""

    def test_should_update_profile_settings(self, client, auth_headers):
        """
        Given: Authenticated user with profile update data
        When: PUT /settings/profile is called
        Then:
            - Returns 200 status code
            - Updated settings are returned
        """
        # Given: Update data
        update_data = {
            "display_name": "테스트 닉네임",
            "timezone": "America/New_York",
            "language": "en"
        }

        # When: PUT /settings/profile
        response = client.put(
            "/settings/profile",
            json=update_data,
            headers=auth_headers
        )

        # Then: Success response with updated data
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["display_name"] == "테스트 닉네임"
        assert data["timezone"] == "America/New_York"
        assert data["language"] == "en"

    def test_should_allow_partial_update(self, client, auth_headers):
        """
        Given: Authenticated user with partial update data
        When: PUT /settings/profile is called
        Then: Only specified fields are updated
        """
        # Given: Only update timezone
        update_data = {"timezone": "Europe/London"}

        # When: PUT /settings/profile
        response = client.put(
            "/settings/profile",
            json=update_data,
            headers=auth_headers
        )

        # Then: Success and timezone updated
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["timezone"] == "Europe/London"


class TestGetNotificationSettings:
    """Test suite for GET /settings/notifications endpoint"""

    def test_should_return_notification_settings(self, client, auth_headers):
        """
        Given: Authenticated user
        When: GET /settings/notifications is called
        Then:
            - Returns 200 status code
            - Default values are set (email_enabled=true, push_enabled=true)
        """
        # When: GET /settings/notifications
        response = client.get("/settings/notifications", headers=auth_headers)

        # Then: Success response with defaults
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["email_enabled"] is True  # Default
        assert data["push_enabled"] is True  # Default
        assert data["frequency"] == "immediate"  # Default


class TestUpdateNotificationSettings:
    """Test suite for PUT /settings/notifications endpoint"""

    def test_should_update_notification_settings(self, client, auth_headers):
        """
        Given: Authenticated user with notification update data
        When: PUT /settings/notifications is called
        Then: Updated settings are returned
        """
        # Given: Update data
        update_data = {
            "email_notifications": False,
            "push_notifications": True,
            "notification_frequency": "daily"
        }

        # When: PUT /settings/notifications
        response = client.put(
            "/settings/notifications",
            json=update_data,
            headers=auth_headers
        )

        # Then: Success response with updated data
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["email_enabled"] is False
        assert data["push_enabled"] is True
        assert data["frequency"] == "daily"

    def test_should_validate_frequency_enum(self, client, auth_headers):
        """
        Given: Invalid notification frequency value
        When: PUT /settings/notifications is called
        Then: Returns 422 validation error
        """
        # Given: Invalid frequency
        update_data = {"notification_frequency": "invalid_value"}

        # When: PUT /settings/notifications
        response = client.put(
            "/settings/notifications",
            json=update_data,
            headers=auth_headers
        )

        # Then: 422 Unprocessable Entity
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdatePrivacySettings:
    """Test suite for PUT /settings/privacy endpoint"""

    def test_should_update_privacy_settings(self, client, auth_headers):
        """
        Given: Authenticated user with privacy update data
        When: PUT /settings/privacy is called
        Then: Returns success message
        """
        # Given: Update data
        update_data = {"profile_visibility": "private"}

        # When: PUT /settings/privacy
        response = client.put(
            "/settings/privacy",
            json=update_data,
            headers=auth_headers
        )

        # Then: Success response
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Privacy settings updated"


class TestGetSecuritySettings:
    """Test suite for GET /settings/security endpoint"""

    def test_should_return_security_settings(self, client, auth_headers):
        """
        Given: Authenticated user
        When: GET /settings/security is called
        Then:
            - Returns 200 status code
            - Default 2FA is disabled
        """
        # When: GET /settings/security
        response = client.get("/settings/security", headers=auth_headers)

        # Then: Success response
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["two_factor_enabled"] is False  # Default


class TestUpdateSecuritySettings:
    """Test suite for PUT /settings/security endpoint"""

    def test_should_update_security_settings(self, client, auth_headers):
        """
        Given: Authenticated user with security update data
        When: PUT /settings/security is called
        Then: Updated settings are returned
        """
        # Given: Enable 2FA
        update_data = {"two_factor_enabled": True}

        # When: PUT /settings/security
        response = client.put(
            "/settings/security",
            json=update_data,
            headers=auth_headers
        )

        # Then: Success response with 2FA enabled
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["two_factor_enabled"] is True


class TestSettingsWithDifferentRoles:
    """Test settings endpoints work for different user roles"""

    def test_client_can_access_settings(self, client, client_auth_headers):
        """
        Given: Authenticated client user
        When: GET /settings is called
        Then: Returns 200 with settings
        """
        response = client.get("/settings", headers=client_auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_detective_can_access_settings(self, client, detective_auth_headers):
        """
        Given: Authenticated detective user
        When: GET /settings is called
        Then: Returns 200 with settings
        """
        response = client.get("/settings", headers=detective_auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_access_settings(self, client, admin_auth_headers):
        """
        Given: Authenticated admin user
        When: GET /settings is called
        Then: Returns 200 with settings
        """
        response = client.get("/settings", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
