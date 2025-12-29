"""
Health Check API Router

Provides liveness and readiness probes for monitoring.
Follows Kubernetes health check patterns for production readiness.
"""
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


# =============================================================================
# Dependency Check Functions (Modular, Extensible)
# =============================================================================

async def check_database(db: Session) -> Dict[str, Any]:
    """
    PostgreSQL 연결 상태 확인

    Args:
        db: SQLAlchemy database session

    Returns:
        Dict with status and latency_ms
    """
    try:
        start = time.perf_counter()
        db.execute(text("SELECT 1"))
        latency_ms = (time.perf_counter() - start) * 1000

        return {
            "status": "ok",
            "latency_ms": round(latency_ms, 2)
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def check_qdrant() -> Dict[str, Any]:
    """
    Qdrant 벡터 DB 연결 상태 확인

    Returns:
        Dict with status and optional latency_ms
    """
    # Skip if Qdrant is not configured
    if not settings.QDRANT_HOST and not settings.QDRANT_URL:
        return {
            "status": "skipped",
            "reason": "Qdrant not configured"
        }

    try:
        from app.utils.qdrant import get_qdrant_client

        start = time.perf_counter()
        client = get_qdrant_client()

        # Simple health check - list collections
        collections = client.get_collections()
        latency_ms = (time.perf_counter() - start) * 1000

        return {
            "status": "ok",
            "latency_ms": round(latency_ms, 2),
            "collections_count": len(collections.collections)
        }
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def check_dynamodb() -> Dict[str, Any]:
    """
    DynamoDB 연결 상태 확인

    Returns:
        Dict with status and table info
    """
    # Skip if DynamoDB table is not configured
    if not settings.DDB_EVIDENCE_TABLE:
        return {
            "status": "skipped",
            "reason": "DynamoDB not configured"
        }

    try:
        import boto3

        start = time.perf_counter()
        dynamodb = boto3.client(
            "dynamodb",
            region_name=settings.AWS_REGION
        )

        # Describe table to verify connection
        response = dynamodb.describe_table(
            TableName=settings.DDB_EVIDENCE_TABLE
        )
        latency_ms = (time.perf_counter() - start) * 1000

        table_status = response.get("Table", {}).get("TableStatus", "UNKNOWN")

        return {
            "status": "ok" if table_status == "ACTIVE" else "degraded",
            "latency_ms": round(latency_ms, 2),
            "table_status": table_status
        }
    except Exception as e:
        logger.error(f"DynamoDB health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# =============================================================================
# Health Check Endpoints
# =============================================================================

@router.get("/health")
async def liveness() -> Dict[str, str]:
    """
    Liveness probe - 서버 생존 확인

    단순히 서버가 응답 가능한지만 확인합니다.
    Kubernetes liveness probe에 사용됩니다.

    Returns:
        {"status": "ok"}
    """
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness probe - 서비스 준비 상태 확인

    모든 의존성(DB, Qdrant, DynamoDB)의 연결 상태를 확인합니다.
    Kubernetes readiness probe에 사용됩니다.

    Returns:
        {
            "status": "ok" | "degraded" | "error",
            "checks": {...},
            "timestamp": "ISO8601"
        }
    """
    checks = {
        "database": await check_database(db),
        "qdrant": await check_qdrant(),
        "dynamodb": await check_dynamodb(),
    }

    # Determine overall status
    statuses = [c["status"] for c in checks.values()]

    if all(s in ("ok", "skipped") for s in statuses):
        overall_status = "ok"
    elif any(s == "error" for s in statuses):
        overall_status = "error"
    else:
        overall_status = "degraded"

    return {
        "status": overall_status,
        "service": "CHAGOK API",
        "version": "0.2.0",
        "environment": settings.APP_ENV,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/detailed")
async def detailed_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    상세 헬스 체크 - 디버깅 및 모니터링용

    readiness와 동일하지만 추가 시스템 정보를 포함합니다.

    Returns:
        상세 시스템 상태 정보
    """
    readiness_result = await readiness(db)

    # Add system info
    import sys
    import platform

    readiness_result["system"] = {
        "python_version": sys.version,
        "platform": platform.platform(),
    }

    return readiness_result
