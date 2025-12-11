"""
Legal Evidence Hub (LEH) - FastAPI Backend
Main application entry point

Version: 0.2.0
Updated: 2025-11-19
"""

import logging  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from mangum import Mangum  # noqa: E402 - AWS Lambda handler

# Import configuration and middleware
from app.core.config import settings  # noqa: E402

# Import API routers
from app.api import (  # noqa: E402
    auth,
    admin,
    assets,
    billing,
    calendar,
    cases,
    client_portal,
    dashboard,
    detective_portal,
    drafts,
    evidence,
    evidence_links,
    lawyer_portal,
    lawyer_clients,
    lawyer_investigators,
    messages,
    party,
    procedure,
    properties,
    relationships,
    search,
    settings as settings_router,
    staff_progress,
    summary,
)
from app.middleware import (  # noqa: E402
    register_exception_handlers,
    SecurityHeadersMiddleware,
    HTTPSRedirectMiddleware,
    AuditLogMiddleware,
    LatencyLoggingMiddleware
)


# ============================================
# Logging Configuration
# ============================================
from app.core.logging_filter import SensitiveDataFilter  # noqa: E402

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Apply sensitive data filter to root logger
root_logger = logging.getLogger()
root_logger.addFilter(SensitiveDataFilter())


# ============================================
# Lifespan Context Manager (Startup/Shutdown)
# ============================================
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Legal Evidence Hub API starting...")
    logger.info("📍 Environment: %s", settings.APP_ENV)
    logger.info("📍 Debug mode: %s", settings.APP_DEBUG)
    logger.info("📍 CORS origins: %s", settings.cors_origins_list)

    # Note: Database connection pool is managed per-request via get_db()
    # Note: AWS services (S3, DynamoDB) currently use mock implementations
    # Note: Qdrant client is initialized on-demand in utils/qdrant.py (in-memory mode for local dev)
    # Note: OpenAI client is initialized on-demand in utils/openai_client.py

    logger.info("✅ Startup complete")

    yield  # Application runs here

    # Shutdown
    logger.info("👋 Legal Evidence Hub API shutting down...")
    # Note: Database connections and logs are automatically cleaned up by FastAPI/SQLAlchemy

    logger.info("✅ Shutdown complete")


# ============================================
# FastAPI Application Instance
# ============================================
app = FastAPI(
    title="Legal Evidence Hub API",
    description="AI 파라리걸 & 증거 허브 백엔드 API - 이혼 사건 전용 증거 분석 및 초안 생성 시스템",
    version="0.2.0",
    docs_url="/docs" if settings.APP_DEBUG else None,  # Disable in production
    redoc_url="/redoc" if settings.APP_DEBUG else None,  # Disable in production
    lifespan=lifespan,  # Modern lifespan handler (replaces on_event)
    contact={
        "name": "Team H·P·L",
        "url": "https://github.com/ORG/REPO",
    }
)


# ============================================
# Middleware Registration (Order matters!)
# ============================================

# 1. HTTPS Redirect (Production only)
app.add_middleware(HTTPSRedirectMiddleware)

# 2. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. Latency Logging Middleware (Logs request duration)
app.add_middleware(LatencyLoggingMiddleware)

# 4. Audit Log Middleware (Must be before CORS to log all requests)
app.add_middleware(AuditLogMiddleware)

# 5. CORS (Must be after security headers and audit log)
# Note: For cross-origin cookie authentication, allow_credentials=True is required
# API Gateway also has CORS config - they should match
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Set-Cookie"]
)

# Note: JWT authentication is handled per-endpoint via get_current_user_id() dependency
# Note: Rate limiting can be added later if needed for production


# ============================================
# Exception Handlers
# ============================================
register_exception_handlers(app)


# ============================================
# Root & Health Check Endpoints
# ============================================
@app.get("/", tags=["Root"])
async def root():
    """
    루트 엔드포인트 - API 정보
    """
    return {
        "service": "Legal Evidence Hub API",
        "version": "0.2.0",
        "environment": settings.APP_ENV,
        "docs": "/docs" if settings.APP_DEBUG else "disabled",
        "health": "/health",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    헬스 체크 엔드포인트

    모니터링 시스템 및 로드밸런서가 서버 상태를 확인하기 위해 사용

    API_SPEC.md 기준:
    - 200 OK: 서버 정상 동작
    - 간단한 응답 형식 (에러 처리 불필요)
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "Legal Evidence Hub API",
            "version": "0.2.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# ============================================
# Router Registration (API Endpoints)
# ============================================
# API 엔드포인트는 app/api/ 디렉토리에 위치 (BACKEND_SERVICE_REPOSITORY_GUIDE.md 기준)

# 인증 라우터
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# 사건 라우터
app.include_router(cases.router, prefix="/cases", tags=["Cases"])

# 재산분할 라우터 (US2 - Asset Division)
app.include_router(assets.router, prefix="/cases/{case_id}/assets", tags=["Assets"])

# 절차 단계 라우터 (US3 - Procedure Stage Tracking)
app.include_router(procedure.router, tags=["Procedure"])
app.include_router(procedure.deadlines_router, tags=["Procedure"])

# 증거 라우터
app.include_router(evidence.router, prefix="/evidence", tags=["Evidence"])

# 초안 라우터 (케이스별 초안 CRUD)
app.include_router(drafts.router, prefix="/cases/{case_id}/drafts", tags=["Drafts"])

# 변호사/스태프 포털 라우터
app.include_router(lawyer_portal.router, prefix="/lawyer", tags=["Lawyer Portal"])
app.include_router(staff_progress.router, tags=["Staff Progress"])

# 변호사 고객 관리 라우터 (005-lawyer-portal-pages US2)
app.include_router(lawyer_clients.router, tags=["Lawyer Clients"])

# 변호사 탐정 관리 라우터 (005-lawyer-portal-pages US3)
app.include_router(lawyer_investigators.router, tags=["Lawyer Investigators"])

# 의뢰인/탐정 포털 라우터
app.include_router(client_portal.router, tags=["Client Portal"])
app.include_router(detective_portal.router, tags=["Detective Portal"])

# 재산분할 라우터 (Phase 1: Property Division)
app.include_router(properties.router, tags=["Properties"])

# 사용자 설정 라우터
app.include_router(settings_router.router, tags=["Settings"])

# 007-lawyer-portal-v1: Party Graph 라우터
app.include_router(party.router, tags=["Party Graph"])
app.include_router(party.graph_router, tags=["Party Graph"])
app.include_router(relationships.router, tags=["Party Relationships"])

# 007-lawyer-portal-v1: Evidence Links 라우터 (US4)
app.include_router(evidence_links.router, tags=["Evidence Links"])

# 007-lawyer-portal-v1: Global Search 라우터 (US6)
app.include_router(search.router, tags=["Search"])

# 007-lawyer-portal-v1: Dashboard (Today View - US7)
app.include_router(dashboard.router, tags=["Dashboard"])

# 메시지 라우터
app.include_router(messages.router, prefix="/messages", tags=["Messages"])

# 청구/결제 라우터
app.include_router(billing.router, tags=["Billing"])
app.include_router(billing.client_router, tags=["Client Billing"])

# Calendar 라우터
app.include_router(calendar.router, tags=["Calendar"])

# Summary 라우터 (US8 - Progress Summary Cards)
app.include_router(summary.router, tags=["Summary"])

# Admin 라우터 (User Management & Audit Log)
app.include_router(admin.router, tags=["Admin"])
# L-work Demo API (테스트 후 제거 가능)
try:
    from app.api.l_demo import router as l_demo_router
    app.include_router(l_demo_router)
except ImportError:
    pass  # l_demo 모듈 없으면 무시


# ============================================
# TEMPORARY: Database Debug Endpoints
# Remove after migration is complete
# ============================================
@app.get("/admin/check-roles", tags=["Admin"])
async def check_roles():
    """Check current role values in database and enum type definition."""
    from app.db.session import get_db
    from sqlalchemy import text

    db = next(get_db())
    try:
        # Check users
        result = db.execute(text("SELECT id, email, role::text as role FROM users"))
        users = [{"id": r[0], "email": r[1], "role": r[2]} for r in result.fetchall()]

        # Check enum type definition
        enum_result = db.execute(text("""
            SELECT e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'userrole'
            ORDER BY e.enumsortorder
        """))
        enum_values = [r[0] for r in enum_result.fetchall()]

        return {
            "users": users,
            "enum_values": enum_values
        }
    finally:
        db.close()


@app.post("/admin/migrate-enums", tags=["Admin"])
async def migrate_enums_to_lowercase():
    """
    Migrate all enum values from uppercase to lowercase.
    Handles: userrole, userstatus, and other enums.
    """
    from app.db.session import get_db
    from sqlalchemy import text

    db = next(get_db())
    try:
        steps = []

        # Migration config: (enum_type, table, column, values)
        migrations = [
            ('userrole', 'users', 'role', ['lawyer', 'staff', 'admin', 'client', 'detective']),
            ('userstatus', 'users', 'status', ['active', 'inactive']),
        ]

        for enum_type, table, column, values in migrations:
            # Step 1: Add lowercase values to enum
            for val in values:
                try:
                    db.execute(text(f"ALTER TYPE {enum_type} ADD VALUE IF NOT EXISTS '{val}'"))
                    steps.append(f"Added {enum_type}.{val}")
                except Exception as e:
                    steps.append(f"Skipped {enum_type}.{val}: {str(e)}")
            db.commit()

            # Step 2: Update from UPPERCASE to lowercase
            for val in values:
                upper_val = val.upper()
                try:
                    result = db.execute(
                        text(f"UPDATE {table} SET {column} = '{val}' WHERE {column}::text = '{upper_val}'")
                    )
                    db.commit()
                    steps.append(f"Updated {result.rowcount} rows: {table}.{column} {upper_val} -> {val}")
                except Exception as e:
                    db.rollback()
                    steps.append(f"Error {table}.{column} {upper_val}: {str(e)}")

        # Verify
        check_result = db.execute(text("SELECT DISTINCT role::text, status::text FROM users"))
        final_values = [{"role": r[0], "status": r[1]} for r in check_result.fetchall()]

        return {
            "status": "success",
            "steps": steps,
            "final_values": final_values
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


# Keep old endpoint for backwards compatibility
@app.post("/admin/migrate-roles", tags=["Admin"])
async def migrate_roles_redirect():
    """Redirects to migrate-enums endpoint."""
    return await migrate_enums_to_lowercase()


# Note: Timeline router removed (002-evidence-timeline feature incomplete)
# Draft preview endpoint (POST /cases/{case_id}/draft-preview) remains in cases router
# Note: RAG search is integrated into draft generation service (draft_service.py)


# ============================================
# AWS Lambda Handler (Mangum)
# ============================================
# Lambda handler for API Gateway
handler = Mangum(app, lifespan="off")


# ============================================
# Development Server (직접 실행 시에만)
# ============================================
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")

    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.APP_DEBUG,  # Auto-reload in debug mode
        log_level=settings.BACKEND_LOG_LEVEL.lower(),
        access_log=True
    )
