"""
Assets API endpoints - US2 재산분할표 (Asset Division Sheet)

GET /cases/{case_id}/assets - List assets for a case
POST /cases/{case_id}/assets - Create a new asset
POST /cases/{case_id}/assets/calculate - Calculate property division
GET /cases/{case_id}/assets/summary - Get asset sheet summary
GET /cases/{case_id}/assets/export - Export assets as CSV
GET /cases/{case_id}/assets/{asset_id} - Get asset detail
PATCH /cases/{case_id}/assets/{asset_id} - Update an asset
DELETE /cases/{case_id}/assets/{asset_id} - Delete an asset

NOTE: Static paths (/calculate, /summary, /export) MUST be defined before
dynamic paths (/{asset_id}) to avoid route conflicts in FastAPI.
"""

from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import io
import csv

from app.db.session import get_db
from app.db.schemas import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
    DivisionCalculateRequest,
    DivisionSummaryResponse,
    AssetSheetSummary,
    AssetCategorySummary,
)
from app.db.models import AssetCategory
from app.services.asset_service import AssetService
from app.core.dependencies import get_current_user_id


router = APIRouter()


# ============================================
# Collection endpoints (no asset_id)
# ============================================

@router.get("", response_model=AssetListResponse)
def list_assets(
    case_id: str,
    category: Optional[AssetCategory] = Query(None, description="Filter by asset category"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all assets for a case

    **Path Parameters:**
    - case_id: Case ID

    **Query Parameters:**
    - category: Filter by asset category (optional)
      - real_estate: 부동산
      - savings: 예금/적금
      - stocks: 주식/증권
      - retirement: 퇴직금/연금
      - vehicle: 차량
      - insurance: 보험
      - debt: 부채
      - other: 기타

    **Response:**
    - 200: List of assets with total count
    - assets: List of asset details
    - total: Total number of assets

    **Errors:**
    - 401: Not authenticated
    - 403: User does not have access to case
    - 404: Case not found

    **Authentication:**
    - Requires valid JWT token
    - User must be a member of the case
    """
    asset_service = AssetService(db)
    assets = asset_service.list_assets(case_id, user_id, category=category)
    return AssetListResponse(assets=assets, total=len(assets))


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    case_id: str,
    asset_data: AssetCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new asset for a case

    **Path Parameters:**
    - case_id: Case ID

    **Request Body:**
    - category: Asset category (required)
    - ownership: Asset ownership - plaintiff/defendant/joint/third_party (required)
    - nature: Asset nature - marital/separate/mixed (default: marital)
    - name: Asset name (required, max 200 chars)
    - current_value: Current value in KRW (required, >= 0)
    - description: Asset description (optional)
    - acquisition_date: Date asset was acquired (optional)
    - acquisition_value: Original acquisition value (optional)
    - valuation_date: Date of valuation (optional)
    - valuation_source: Source of valuation (e.g., KB시세) (optional)
    - division_ratio_plaintiff: Plaintiff's division ratio 0-100 (default: 50)
    - division_ratio_defendant: Defendant's division ratio 0-100 (default: 50)
    - proposed_allocation: Proposed final ownership (optional)
    - evidence_id: Link to supporting evidence (optional)
    - notes: Additional notes (optional)

    **Response:**
    - 201: Asset created successfully
    - Returns created asset details

    **Errors:**
    - 401: Not authenticated
    - 403: User does not have access to case
    - 404: Case not found
    - 422: Validation error

    **Authentication:**
    - Requires valid JWT token
    - User must be a member of the case
    """
    asset_service = AssetService(db)
    return asset_service.create_asset(case_id, asset_data, user_id)


# ============================================
# Static path endpoints (MUST be before /{asset_id})
# ============================================

@router.post("/calculate", response_model=DivisionSummaryResponse)
def calculate_division(
    case_id: str,
    request: DivisionCalculateRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Calculate property division for a case

    **Path Parameters:**
    - case_id: Case ID

    **Request Body:**
    - plaintiff_ratio: Plaintiff's division ratio 0-100 (default: 50)
    - defendant_ratio: Defendant's division ratio 0-100 (default: 50)
    - include_separate: Include separate property in calculation (default: false)
    - notes: Optional notes for this calculation

    **Response:**
    - 200: Division calculation result
    - total_marital_assets: Total value of marital assets
    - total_separate_plaintiff: Plaintiff's separate property total
    - total_separate_defendant: Defendant's separate property total
    - total_debts: Total debts
    - net_marital_value: Net marital value (assets - debts)
    - plaintiff_share: Plaintiff's calculated share
    - defendant_share: Defendant's calculated share
    - settlement_amount: Settlement amount (정산금)
      - Positive: Plaintiff pays defendant
      - Negative: Defendant pays plaintiff
    - plaintiff_holdings: What plaintiff currently holds
    - defendant_holdings: What defendant currently holds

    **Errors:**
    - 401: Not authenticated
    - 403: User does not have access to case
    - 404: Case not found
    - 422: Validation error

    **Authentication:**
    - Requires valid JWT token
    - User must be a member of the case

    **Korean Legal Reference:**
    - 민법 제839조의2 (재산분할청구권)
    - 혼인 중 취득한 재산은 공동재산으로 추정
    - 기여도에 따라 분할 비율 결정 (기본 50:50)
    """
    asset_service = AssetService(db)
    return asset_service.calculate_division(
        case_id=case_id,
        user_id=user_id,
        plaintiff_ratio=request.plaintiff_ratio,
        defendant_ratio=request.defendant_ratio,
        include_separate=request.include_separate,
        notes=request.notes
    )


@router.get("/summary", response_model=AssetSheetSummary)
def get_asset_summary(
    case_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get complete asset sheet summary

    **Path Parameters:**
    - case_id: Case ID

    **Response:**
    - 200: Asset sheet summary
    - division_summary: Latest division calculation result (may be null)
    - category_summaries: Asset totals by category
    - total_assets: Total number of assets

    **Errors:**
    - 401: Not authenticated
    - 403: User does not have access to case
    - 404: Case not found

    **Authentication:**
    - Requires valid JWT token
    - User must be a member of the case
    """
    asset_service = AssetService(db)
    summary = asset_service.get_asset_sheet_summary(case_id, user_id)

    # Convert to response model
    return AssetSheetSummary(
        division_summary=summary["division_summary"],
        category_summaries=[
            AssetCategorySummary(**cat) for cat in summary["category_summaries"]
        ],
        total_assets=summary["total_assets"]
    )


@router.get("/export")
def export_assets(
    case_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Export assets as CSV file

    **Path Parameters:**
    - case_id: Case ID

    **Response:**
    - 200: CSV file download
    - Content-Type: text/csv
    - Content-Disposition: attachment; filename="assets_{case_id}.csv"

    **Errors:**
    - 401: Not authenticated
    - 403: User does not have access to case
    - 404: Case not found

    **Authentication:**
    - Requires valid JWT token
    - User must be a member of the case

    **Note:**
    This exports a basic CSV. For Excel format with formatting,
    additional dependencies (openpyxl) would be required.
    """
    asset_service = AssetService(db)
    assets = asset_service.list_assets(case_id, user_id)

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header (Korean)
    writer.writerow([
        "ID",
        "분류",
        "소유자",
        "재산성격",
        "명칭",
        "현재가치(원)",
        "취득가액(원)",
        "취득일",
        "감정기관",
        "원고비율(%)",
        "피고비율(%)",
        "비고"
    ])

    # Category and ownership translations
    category_names = {
        "real_estate": "부동산",
        "savings": "예금/적금",
        "stocks": "주식/증권",
        "retirement": "퇴직금/연금",
        "vehicle": "차량",
        "insurance": "보험",
        "debt": "부채",
        "other": "기타"
    }
    ownership_names = {
        "plaintiff": "원고",
        "defendant": "피고",
        "joint": "공동",
        "third_party": "제3자"
    }
    nature_names = {
        "marital": "공동재산",
        "separate": "특유재산",
        "mixed": "혼합재산"
    }

    # Write data rows
    for asset in assets:
        writer.writerow([
            asset.id,
            category_names.get(asset.category.value, asset.category.value),
            ownership_names.get(asset.ownership.value, asset.ownership.value),
            nature_names.get(asset.nature.value, asset.nature.value),
            asset.name,
            asset.current_value,
            asset.acquisition_value or "",
            asset.acquisition_date.strftime("%Y-%m-%d") if asset.acquisition_date else "",
            asset.valuation_source or "",
            asset.division_ratio_plaintiff or 50,
            asset.division_ratio_defendant or 50,
            asset.notes or ""
        ])

    # Prepare response
    output.seek(0)
    content = output.getvalue()

    # Return as streaming response with BOM for Excel compatibility
    return StreamingResponse(
        io.BytesIO(('\ufeff' + content).encode('utf-8-sig')),
        media_type="text/csv; charset=utf-8-sig",
        headers={
            "Content-Disposition": f'attachment; filename="assets_{case_id}.csv"'
        }
    )


# ============================================
# Dynamic path endpoints (/{asset_id})
# ============================================

@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    case_id: str,
    asset_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get asset detail by ID

    **Path Parameters:**
    - case_id: Case ID
    - asset_id: Asset ID

    **Response:**
    - 200: Asset detail

    **Errors:**
    - 401: Not authenticated
    - 403: User does not have access to case
    - 404: Asset or case not found

    **Authentication:**
    - Requires valid JWT token
    - User must be a member of the case
    """
    asset_service = AssetService(db)
    return asset_service.get_asset(case_id, asset_id, user_id)


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    case_id: str,
    asset_id: str,
    update_data: AssetUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update an asset

    **Path Parameters:**
    - case_id: Case ID
    - asset_id: Asset ID

    **Request Body:**
    All fields are optional - only provided fields will be updated
    - category, ownership, nature, name, description
    - acquisition_date, acquisition_value, current_value
    - valuation_date, valuation_source
    - division_ratio_plaintiff, division_ratio_defendant
    - proposed_allocation, evidence_id, notes

    **Response:**
    - 200: Updated asset detail

    **Errors:**
    - 401: Not authenticated
    - 403: User does not have write permission
    - 404: Asset or case not found
    - 422: Validation error

    **Authentication:**
    - Requires valid JWT token
    - User must be a member of the case
    """
    asset_service = AssetService(db)
    return asset_service.update_asset(case_id, asset_id, update_data, user_id)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    case_id: str,
    asset_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete an asset

    **Path Parameters:**
    - case_id: Case ID
    - asset_id: Asset ID

    **Response:**
    - 204: Asset deleted successfully (no content)

    **Errors:**
    - 401: Not authenticated
    - 403: User does not have write permission
    - 404: Asset or case not found

    **Authentication:**
    - Requires valid JWT token
    - User must be a member of the case
    """
    asset_service = AssetService(db)
    asset_service.delete_asset(case_id, asset_id, user_id)
    return None
