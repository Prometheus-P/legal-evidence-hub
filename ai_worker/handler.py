"""Entry point for AI pipeline worker (e.g., Lambda handler or ECS task)."""

from datetime import datetime
from typing import Any, Dict


def handle(event: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Stub handler that documents expected payload structure."""
    case_id = event.get("case_id", "UNKNOWN")
    drive_url = event.get("drive_url")
    requested_at = event.get("requested_at", datetime.utcnow().isoformat())

    return {
        "case_id": case_id,
        "drive_url": drive_url,
        "status": "received",
        "requested_at": requested_at,
        "notes": "Implement ingestion + AI processing pipeline here.",
    }
