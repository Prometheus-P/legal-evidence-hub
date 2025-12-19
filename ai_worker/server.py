"""
AI Worker Local Development Server
FastAPI 서버 - 로컬 개발 및 테스트용
프로덕션에서는 Lambda handler.py 사용
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LEH AI Worker",
    description="Legal Evidence Hub AI Processing Service",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Schemas
# ============================================

class KeypointExtractionRequest(BaseModel):
    case_id: str
    evidence_file_ids: Optional[List[str]] = None
    use_fast_path: bool = True
    use_gpt: bool = True


class ExtractedKeypoint(BaseModel):
    statement: str
    confidence_score: float
    type_code: str
    legal_ground_codes: List[str]
    evidence_extracts: List[dict] = []


class KeypointExtractionResponse(BaseModel):
    case_id: str
    keypoints: List[ExtractedKeypoint]
    errors: List[str] = []


# ============================================
# Endpoints
# ============================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai_worker"}


@app.post("/api/v1/keypoints/extract", response_model=KeypointExtractionResponse)
async def extract_keypoints(request: KeypointExtractionRequest):
    """
    증거에서 핵심 쟁점 추출
    """
    from src.analysis.keypoint_extractor import KeypointExtractor
    from src.storage.metadata_store import MetadataStore
    
    errors = []
    extracted = []
    
    try:
        # OpenAI API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        
        # MetadataStore에서 증거 청크 조회
        metadata_store = MetadataStore()
        
        # case_id로 증거 파일 조회
        evidence_files = metadata_store.get_evidence_by_case(request.case_id)
        
        if request.evidence_file_ids:
            evidence_files = [
                ef for ef in evidence_files 
                if ef.file_id in request.evidence_file_ids
            ]
        
        if not evidence_files:
            logger.warning(f"No evidence files found for case {request.case_id}")
            return KeypointExtractionResponse(
                case_id=request.case_id,
                keypoints=[],
                errors=["No evidence files found"]
            )
        
        # KeypointExtractor 초기화
        extractor = KeypointExtractor(
            openai_api_key=api_key,
            use_fast_path=request.use_fast_path,
            use_gpt_extraction=request.use_gpt,
        )
        
        # 각 파일의 청크에서 쟁점 추출
        all_chunks = []
        for ef in evidence_files:
            chunks = metadata_store.get_chunks_by_file(ef.file_id)
            all_chunks.extend(chunks)
        
        if not all_chunks:
            logger.warning(f"No chunks found for case {request.case_id}")
            return KeypointExtractionResponse(
                case_id=request.case_id,
                keypoints=[],
                errors=["No evidence chunks found"]
            )
        
        # 쟁점 추출
        result = extractor.extract(all_chunks)
        
        # 응답 변환
        for kp in result.keypoints:
            extracted.append(ExtractedKeypoint(
                statement=kp.statement,
                confidence_score=kp.confidence_score,
                type_code="FACT",  # 기본값
                legal_ground_codes=kp.legal_ground_codes,
                evidence_extracts=[
                    ext.model_dump() for ext in kp.evidence_extracts
                ],
            ))
        
        errors.extend(result.errors)
        
    except Exception as e:
        logger.error(f"Keypoint extraction failed: {e}")
        errors.append(str(e))
    
    return KeypointExtractionResponse(
        case_id=request.case_id,
        keypoints=extracted,
        errors=errors,
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AI_WORKER_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
