"""
Draft Formatter Module
프롬프트 포매팅 및 인용 추출
"""

from typing import List

from app.db.schemas import DraftCitation


def format_rag_context(rag_results: List[dict]) -> str:
    """
    Format RAG search results for GPT-4o prompt

    Args:
        rag_results: List of evidence documents from RAG search

    Returns:
        Formatted context string
    """
    if not rag_results:
        return "(증거 자료 없음 - 기본 템플릿으로 작성)"

    context_parts = []
    for i, doc in enumerate(rag_results, start=1):
        evidence_id = doc.get("id", f"evidence_{i}")
        content = doc.get("content", "")
        labels = doc.get("labels", [])
        speaker = doc.get("speaker", "")
        timestamp = doc.get("timestamp", "")

        # Truncate content if too long
        if len(content) > 500:
            content = content[:500] + "..."

        context_parts.append(f"""
[증거 {i}] (ID: {evidence_id})
- 분류: {", ".join(labels) if labels else "N/A"}
- 화자: {speaker or "N/A"}
- 시점: {timestamp or "N/A"}
- 내용: {content}
""")

    return "\n".join(context_parts)


def build_draft_prompt(
    case,
    sections: List[str],
    rag_context: List[dict],
    language: str,
    style: str
) -> List[dict]:
    """
    Build GPT-4o prompt with RAG context

    Args:
        case: Case object
        sections: Sections to generate
        rag_context: RAG search results
        language: Language (ko/en)
        style: Writing style

    Returns:
        List of messages for GPT-4o
    """
    # System message - define role and constraints
    system_message = {
        "role": "system",
        "content": """당신은 대한민국의 전문 법률가입니다.
이혼 소송 준비서면 초안을 작성하는 AI 어시스턴트입니다.

**중요 원칙:**
1. 제공된 증거만을 기반으로 작성하세요
2. 추측이나 가정을 하지 마세요
3. 법률 용어를 정확하게 사용하세요
4. 민법 제840조 이혼 사유를 정확히 인용하세요
5. 존중하고 전문적인 어조를 유지하세요

**작성 형식:**
- 법원 제출용 표준 형식
- 명확한 섹션 구분
- 증거 기반 서술
- 법률 근거 명시

**주의사항:**
본 문서는 초안이며, 변호사의 검토가 필수입니다.
"""
    }

    # Build RAG context string
    rag_context_str = format_rag_context(rag_context)

    # User message - include case info and RAG context
    user_message = {
        "role": "user",
        "content": f"""
다음 정보를 바탕으로 이혼 소송 준비서면 초안을 작성해 주세요.

**사건 정보:**
- 사건명: {case.title}
- 사건 설명: {case.description or "N/A"}

**생성할 섹션:**
{", ".join(sections)}

**증거 자료 (RAG 검색 결과):**
{rag_context_str}

**요청사항:**
- 언어: {language}
- 스타일: {style}
- 위 증거를 기반으로 법률적 논리를 구성해 주세요
- 각 주장에 대해 증거 번호를 명시해 주세요 (예: [증거 1], [증거 2])

준비서면 초안을 작성해 주세요.
"""
    }

    return [system_message, user_message]


def extract_citations(rag_results: List[dict]) -> List[DraftCitation]:
    """
    Extract citations from RAG results

    Args:
        rag_results: List of evidence documents from RAG search

    Returns:
        List of DraftCitation objects
    """
    citations = []

    for doc in rag_results:
        evidence_id = doc.get("id")
        content = doc.get("content", "")
        labels = doc.get("labels", [])

        # Create snippet (first 200 chars)
        snippet = content[:200] + "..." if len(content) > 200 else content

        citations.append(
            DraftCitation(
                evidence_id=evidence_id,
                snippet=snippet,
                labels=labels
            )
        )

    return citations
