"""
Detective Earnings Repository - Data access layer for DetectiveEarnings model
009-mvp-gap-closure - US11 (FR-040)
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal

from app.db.models import DetectiveEarnings, EarningsStatus


class DetectiveEarningsRepository:
    """Repository for DetectiveEarnings database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        detective_id: str,
        case_id: str,
        amount: int,
        description: Optional[str] = None
    ) -> DetectiveEarnings:
        """
        Create a new earnings record.

        Args:
            detective_id: ID of the detective
            case_id: ID of the case
            amount: Amount in KRW (원 단위)
            description: Optional description

        Returns:
            Created DetectiveEarnings record
        """
        earnings = DetectiveEarnings(
            detective_id=detective_id,
            case_id=case_id,
            amount=amount,
            description=description,
            status=EarningsStatus.PENDING
        )
        self.db.add(earnings)
        self.db.commit()
        self.db.refresh(earnings)
        return earnings

    def get_by_id(self, earnings_id: str) -> Optional[DetectiveEarnings]:
        """Get earnings record by ID"""
        return self.db.query(DetectiveEarnings).filter(
            DetectiveEarnings.id == earnings_id
        ).first()

    def get_by_detective_id(
        self,
        detective_id: str,
        status: Optional[EarningsStatus] = None,
        limit: int = 100
    ) -> List[DetectiveEarnings]:
        """
        Get all earnings records for a detective.

        Args:
            detective_id: ID of the detective
            status: Optional status filter
            limit: Maximum number of records to return

        Returns:
            List of DetectiveEarnings records
        """
        query = self.db.query(DetectiveEarnings).filter(
            DetectiveEarnings.detective_id == detective_id
        )

        if status:
            query = query.filter(DetectiveEarnings.status == status)

        return query.order_by(desc(DetectiveEarnings.created_at)).limit(limit).all()

    def get_by_case_id(
        self,
        case_id: str,
        status: Optional[EarningsStatus] = None
    ) -> List[DetectiveEarnings]:
        """
        Get all earnings records for a case.

        Args:
            case_id: ID of the case
            status: Optional status filter

        Returns:
            List of DetectiveEarnings records
        """
        query = self.db.query(DetectiveEarnings).filter(
            DetectiveEarnings.case_id == case_id
        )

        if status:
            query = query.filter(DetectiveEarnings.status == status)

        return query.order_by(desc(DetectiveEarnings.created_at)).all()

    def get_total_earnings(
        self,
        detective_id: str,
        status: Optional[EarningsStatus] = None
    ) -> Decimal:
        """
        Get total earnings for a detective.

        Args:
            detective_id: ID of the detective
            status: Optional status filter (e.g., only PAID earnings)

        Returns:
            Total earnings as Decimal
        """
        query = self.db.query(func.sum(DetectiveEarnings.amount)).filter(
            DetectiveEarnings.detective_id == detective_id
        )

        if status:
            query = query.filter(DetectiveEarnings.status == status)

        total = query.scalar()
        return Decimal(total or 0)

    def get_pending_total(self, detective_id: str) -> Decimal:
        """Get total pending (unpaid) earnings for a detective."""
        return self.get_total_earnings(detective_id, EarningsStatus.PENDING)

    def get_paid_total(self, detective_id: str) -> Decimal:
        """Get total paid earnings for a detective."""
        return self.get_total_earnings(detective_id, EarningsStatus.PAID)

    def mark_as_paid(
        self,
        earnings_id: str,
        paid_at: Optional[datetime] = None
    ) -> Optional[DetectiveEarnings]:
        """
        Mark an earnings record as paid.

        Args:
            earnings_id: ID of the earnings record
            paid_at: Optional payment datetime (defaults to now)

        Returns:
            Updated DetectiveEarnings record or None if not found
        """
        earnings = self.get_by_id(earnings_id)
        if not earnings:
            return None

        earnings.status = EarningsStatus.PAID
        earnings.paid_at = paid_at or datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(earnings)
        return earnings

    def update(
        self,
        earnings_id: str,
        amount: Optional[int] = None,
        description: Optional[str] = None
    ) -> Optional[DetectiveEarnings]:
        """
        Update an earnings record.

        Args:
            earnings_id: ID of the earnings record
            amount: New amount (optional)
            description: New description (optional)

        Returns:
            Updated DetectiveEarnings record or None if not found
        """
        earnings = self.get_by_id(earnings_id)
        if not earnings:
            return None

        if amount is not None:
            earnings.amount = amount
        if description is not None:
            earnings.description = description

        self.db.commit()
        self.db.refresh(earnings)
        return earnings

    def delete(self, earnings_id: str) -> bool:
        """
        Delete an earnings record.

        Args:
            earnings_id: ID of the earnings record

        Returns:
            True if deleted, False if not found
        """
        earnings = self.get_by_id(earnings_id)
        if not earnings:
            return False

        self.db.delete(earnings)
        self.db.commit()
        return True

    def get_earnings_summary(self, detective_id: str) -> dict:
        """
        Get earnings summary for a detective.

        Args:
            detective_id: ID of the detective

        Returns:
            Dictionary with total, pending, and paid amounts
        """
        total = self.get_total_earnings(detective_id)
        pending = self.get_pending_total(detective_id)
        paid = self.get_paid_total(detective_id)

        return {
            "total": total,
            "pending": pending,
            "paid": paid
        }
