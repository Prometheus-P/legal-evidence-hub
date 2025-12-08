"""Repository for case checklist status persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.db.models import CaseChecklistStatus


class CaseChecklistRepository:
    """Provides CRUD helpers for per-case feedback checklist states."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_status_map(self, case_id: str) -> Dict[str, CaseChecklistStatus]:
        """Return a mapping of checklist item_id -> status rows for the case."""
        rows = (
            self.session.query(CaseChecklistStatus)
            .filter(CaseChecklistStatus.case_id == case_id)
            .all()
        )
        return {row.item_id: row for row in rows}

    def set_status(
        self,
        *,
        case_id: str,
        item_id: str,
        status: str,
        updated_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> CaseChecklistStatus:
        """Upsert checklist status for a case. Caller is responsible for committing."""
        record = (
            self.session.query(CaseChecklistStatus)
            .filter(
                CaseChecklistStatus.case_id == case_id,
                CaseChecklistStatus.item_id == item_id,
            )
            .one_or_none()
        )

        if record is None:
            record = CaseChecklistStatus(
                case_id=case_id,
                item_id=item_id,
                status=status,
                notes=notes,
                updated_by=updated_by,
            )
            self.session.add(record)
        else:
            record.status = status
            record.notes = notes
            record.updated_by = updated_by
            record.updated_at = datetime.now(timezone.utc)

        return record
