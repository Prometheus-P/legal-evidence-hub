"""
Precedent search utilities for 012-precedent-integration feature.

This module extends qdrant.py with precedent-specific search functionality.
"""

import logging
from typing import List, Dict
from qdrant_client.http.models import Distance, VectorParams

from app.utils.qdrant import (
    _get_qdrant_client,
    LEGAL_KNOWLEDGE_COLLECTION,
)
from app.utils.openai_client import generate_embedding
from qdrant_client.http import models

logger = logging.getLogger(__name__)


def create_legal_knowledge_collection() -> bool:
    """
    Create the legal knowledge collection for precedent search.
    T004: Initialize leh_legal_knowledge collection with 1536-dim vectors.

    Returns:
        True if created or already exists, False on error
    """
    client = _get_qdrant_client()

    try:
        collections = client.get_collections().collections
        if any(c.name == LEGAL_KNOWLEDGE_COLLECTION for c in collections):
            logger.info(f"Legal knowledge collection {LEGAL_KNOWLEDGE_COLLECTION} already exists")
            return True

        client.create_collection(
            collection_name=LEGAL_KNOWLEDGE_COLLECTION,
            vectors_config=VectorParams(
                size=1536,  # text-embedding-3-small dimension
                distance=Distance.COSINE
            )
        )
        logger.info(f"Created legal knowledge collection: {LEGAL_KNOWLEDGE_COLLECTION}")
        return True

    except Exception as e:
        logger.error(f"Error creating legal knowledge collection: {e}")
        return False


def search_similar_precedents(
    query: str,
    limit: int = 10,
    min_score: float = 0.5
) -> List[Dict]:
    """
    Search for similar precedents using semantic similarity.

    Args:
        query: Search query (typically fault types or case summary)
        limit: Maximum number of results to return
        min_score: Minimum similarity score threshold (0-1)

    Returns:
        List of precedent cases with similarity scores
    """
    client = _get_qdrant_client()

    try:
        # Check if collection exists
        collections = client.get_collections().collections
        if not any(c.name == LEGAL_KNOWLEDGE_COLLECTION for c in collections):
            logger.warning(f"Legal knowledge collection {LEGAL_KNOWLEDGE_COLLECTION} does not exist")
            return []

        # Generate query embedding
        query_embedding = generate_embedding(query)

        # Filter for case_law documents only
        qdrant_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="doc_type",
                    match=models.MatchValue(value="case_law")
                )
            ]
        )

        # Execute search with score threshold
        results = client.query_points(
            collection_name=LEGAL_KNOWLEDGE_COLLECTION,
            query=query_embedding,
            query_filter=qdrant_filter,
            limit=limit,
            with_payload=True,
            score_threshold=min_score
        ).points

        # Parse results into precedent format
        precedents = []
        for hit in results:
            payload = hit.payload or {}
            # document 필드가 실제 판결 요지를 담고 있음 (Qdrant 데이터 구조)
            summary = payload.get("summary") or payload.get("document") or payload.get("content", "")
            precedent = {
                "case_ref": payload.get("case_number", payload.get("case_ref", "")),
                "court": payload.get("court", ""),
                "decision_date": payload.get("decision_date", ""),
                "summary": summary,
                "division_ratio": payload.get("division_ratio"),
                "key_factors": payload.get("key_factors", []),
                "similarity_score": round(hit.score, 3) if hit.score else 0
            }
            precedents.append(precedent)

        logger.info(f"Found {len(precedents)} similar precedents for query: {query[:50]}...")
        return precedents

    except Exception as e:
        logger.error(f"Error searching similar precedents: {e}")
        return []


def get_fallback_precedents(fault_types: List[str] = None) -> List[Dict]:
    """
    Return fallback sample precedents based on fault types.

    Args:
        fault_types: 유책사유 목록 (한글). None이면 기본 상위 3개 반환.

    Returns:
        해당 유책사유와 관련된 판례 Mock 데이터
    """
    # 유형별 판례 Mock 데이터
    ALL_FALLBACKS = [
        # 부정행위 관련
        {
            "case_ref": "2020므12345",
            "court": "서울가정법원",
            "decision_date": "2020-05-15",
            "summary": "배우자의 부정행위와 장기간 별거로 인한 혼인관계 파탄. 재산분할에서 기여도를 인정하여 원고에게 60% 배분.",
            "division_ratio": {"plaintiff": 60, "defendant": 40},
            "key_factors": ["부정행위", "별거", "기여도"],
            "similarity_score": 0.85
        },
        {
            "case_ref": "2021므11111",
            "court": "서울가정법원",
            "decision_date": "2021-02-20",
            "summary": "배우자의 외도로 인한 이혼 청구. 위자료 5천만원 인정.",
            "division_ratio": {"plaintiff": 55, "defendant": 45},
            "key_factors": ["부정행위", "외도", "위자료"],
            "similarity_score": 0.82
        },
        # 가정폭력 관련
        {
            "case_ref": "2019므98765",
            "court": "서울가정법원",
            "decision_date": "2019-11-20",
            "summary": "가정폭력으로 인한 혼인관계 파탄. 피고의 유책사유 인정, 위자료 3천만원 판결.",
            "division_ratio": {"plaintiff": 55, "defendant": 45},
            "key_factors": ["가정폭력", "위자료", "유책사유"],
            "similarity_score": 0.78
        },
        {
            "case_ref": "2020므22222",
            "court": "인천가정법원",
            "decision_date": "2020-08-10",
            "summary": "상습적 폭력으로 인한 이혼. 양육권은 원고에게, 위자료 4천만원.",
            "division_ratio": {"plaintiff": 60, "defendant": 40},
            "key_factors": ["가정폭력", "양육권", "상습폭력"],
            "similarity_score": 0.75
        },
        # 악의의 유기 관련
        {
            "case_ref": "2021므33333",
            "court": "수원가정법원",
            "decision_date": "2021-06-15",
            "summary": "배우자가 3년간 가출하여 생활비 미지급. 악의의 유기로 이혼 인정.",
            "division_ratio": {"plaintiff": 65, "defendant": 35},
            "key_factors": ["악의의 유기", "생활비", "가출"],
            "similarity_score": 0.80
        },
        # 재정 비행 관련
        {
            "case_ref": "2020므44444",
            "court": "서울가정법원",
            "decision_date": "2020-12-05",
            "summary": "도박으로 인한 가정경제 파탄. 재산분할에서 피고 과실 인정.",
            "division_ratio": {"plaintiff": 70, "defendant": 30},
            "key_factors": ["재정 비행", "도박", "채무"],
            "similarity_score": 0.73
        },
        # 혼인지속 곤란 관련
        {
            "case_ref": "2021므54321",
            "court": "인천가정법원",
            "decision_date": "2021-03-10",
            "summary": "성격차이 및 경제적 갈등으로 인한 이혼. 양 당사자 과실 인정, 재산분할 5:5.",
            "division_ratio": {"plaintiff": 50, "defendant": 50},
            "key_factors": ["혼인지속 곤란", "성격차이", "경제적 갈등"],
            "similarity_score": 0.72
        },
        {
            "case_ref": "2019므55555",
            "court": "대전가정법원",
            "decision_date": "2019-09-25",
            "summary": "장기간 별거 후 혼인관계 회복 불가. 재산분할 및 양육비 결정.",
            "division_ratio": {"plaintiff": 50, "defendant": 50},
            "key_factors": ["별거", "혼인지속 곤란", "양육비"],
            "similarity_score": 0.70
        },
    ]

    # 유책사유가 없으면 상위 3개 반환
    if not fault_types:
        logger.info("No fault_types provided, returning default fallback precedents")
        return ALL_FALLBACKS[:3]

    # 유책사유와 매칭되는 판례 필터링
    matched = []
    for precedent in ALL_FALLBACKS:
        key_factors = precedent.get("key_factors", [])
        # 유책사유와 key_factors 매칭
        for ft in fault_types:
            if ft in key_factors or any(ft in kf for kf in key_factors):
                matched.append(precedent)
                break

    # 매칭된 결과가 있으면 반환, 없으면 기본 3개
    if matched:
        # 유사도 점수로 정렬
        matched.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        logger.info(f"Fallback matched {len(matched)} precedents for fault_types={fault_types}")
        return matched[:5]

    logger.info(f"No matching fallback for fault_types={fault_types}, returning default")
    return ALL_FALLBACKS[:3]
