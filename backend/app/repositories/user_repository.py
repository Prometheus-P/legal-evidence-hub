"""
User Repository - Data access layer for User model
Per BACKEND_SERVICE_REPOSITORY_GUIDE.md pattern
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import User, UserRole
from app.core.security import hash_password


class UserRepository:
    """
    Repository for User model database operations
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address

        Args:
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        return self.session.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID

        Args:
            user_id: User's ID

        Returns:
            User object if found, None otherwise
        """
        return self.session.query(User).filter(User.id == user_id).first()

    def create(self, email: str, password: str, name: str, role: UserRole = UserRole.LAWYER) -> User:
        """
        Create a new user

        Args:
            email: User's email
            password: Plain text password (will be hashed)
            name: User's name
            role: User's role (default: LAWYER)

        Returns:
            Created User object
        """
        hashed_password = hash_password(password)

        user = User(
            email=email,
            hashed_password=hashed_password,
            name=name,
            role=role
        )

        self.session.add(user)
        self.session.flush()  # Get ID without committing transaction

        return user

    def exists(self, email: str) -> bool:
        """
        Check if user with email exists

        Args:
            email: User's email

        Returns:
            True if user exists, False otherwise
        """
        return self.session.query(User).filter(User.email == email).count() > 0
