"""
LSSP API Module (v2.01-v2.15)
Legal Service Standardization Protocol API routers
"""

from fastapi import APIRouter

from .legal_grounds import router as legal_grounds_router
from .keypoints import router as keypoints_router
from .drafts import router as drafts_router
from .pipeline import router as pipeline_router

# Main LSSP router
router = APIRouter(prefix="/lssp", tags=["LSSP"])

# Include sub-routers
router.include_router(legal_grounds_router)
router.include_router(keypoints_router)
router.include_router(drafts_router)
router.include_router(pipeline_router)

__all__ = ["router"]
