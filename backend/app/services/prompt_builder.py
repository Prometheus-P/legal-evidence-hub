"""
Prompt Builder Service - Constructs GPT-4o prompts for draft generation

Extracted from DraftService God Class (Phase 13 refactoring)
Handles prompt construction with evidence and legal context injection.
"""

from typing import List, Any

from app.utils.qdrant import get_template_schema_for_prompt
from app.services.rag_orchestrator import RAGOrchestrator


class PromptBuilder:
    """
    Builds structured prompts for GPT-4o draft generation.

    Responsibilities:
    - Construct system prompts with legal writing guidelines
    - Build user prompts with case info and RAG context
    - Support both JSON schema and plain text output modes
    """

    def __init__(self, rag_orchestrator: RAGOrchestrator = None):
        """
        Initialize PromptBuilder.

        Args:
            rag_orchestrator: Optional RAGOrchestrator for context formatting
        """
        self.rag = rag_orchestrator or RAGOrchestrator()

    def build_draft_prompt(
        self,
        case: Any,
        sections: List[str],
        evidence_context: List[dict],
        legal_context: List[dict],
        language: str = "ko",
        style: str = "formal"
    ) -> List[dict]:
        """
        Build GPT-4o prompt with evidence and legal RAG context.

        Args:
            case: Case object with title and description
            sections: Sections to generate (e.g., ["청구원인", "청구취지"])
            evidence_context: Evidence RAG search results
            legal_context: Legal knowledge RAG search results
            language: Language code (ko/en)
            style: Writing style (formal/informal)

        Returns:
            List of messages for GPT-4o API call
        """
        # Try to get template schema from Qdrant
        template_schema = get_template_schema_for_prompt("이혼소장")
        use_json_output = template_schema is not None

        # Build system message
        system_message = self._build_system_message(template_schema, use_json_output)

        # Format contexts using RAG orchestrator
        evidence_context_str = self.rag.format_evidence_context(evidence_context)
        legal_context_str = self.rag.format_legal_context(legal_context)

        # Build user message
        user_message = self._build_user_message(
            case=case,
            sections=sections,
            evidence_context_str=evidence_context_str,
            legal_context_str=legal_context_str,
            language=language,
            style=style,
            use_json_output=use_json_output
        )

        return [system_message, user_message]

    def _build_system_message(self, template_schema: str, use_json_output: bool) -> dict:
        """
        Build system message with role definition and output format.

        Args:
            template_schema: JSON schema string for structured output
            use_json_output: Whether to use JSON output mode

        Returns:
            System message dict for GPT-4o
        """
        if use_json_output:
            return {
                "role": "system",
                "content": f"""당신은 대한민국 가정법원에 제출하는 정식 소장(訴狀)을 작성하는 전문 법률가입니다.

[핵심 원칙 - 반드시 준수]
1. 모든 사실관계, 날짜, 발언 내용은 오직 제공된 "증거 자료"에서만 추출하세요
2. 증거에 없는 내용을 임의로 생성하거나 추측하지 마세요
3. 확인되지 않은 정보는 "확인 필요" 또는 "[미확인]"으로 표시하세요

[출력 형식 - 중요!]
- 반드시 아래 JSON 스키마에 맞춰 출력하세요
- 유효한 JSON 형식으로만 응답하세요 (추가 설명 없이 JSON만)
- 각 섹션의 format 객체는 문서 형식 정보입니다 (들여쓰기, 정렬, 줄간격 등)

[JSON 스키마]
{template_schema}

[증거 인용 방식]
- grounds 섹션의 각 paragraph에 evidence_refs 배열로 증거 번호 포함
- 예: "evidence_refs": ["갑 제1호증", "갑 제2호증"]
- 날짜, 시간, 발언 내용은 증거에서 그대로 가져올 것

[금액 산정]
- 위자료: 증거에서 확인된 유책행위 정도 기반
- 지연손해금: 연 12% (소송촉진법 제3조)

[법적 근거]
- grounds 섹션의 "이혼 사유" 부분에 legal_basis 객체로 민법 제840조 인용

※ AI 생성 초안이며 변호사 검토 필수
"""
            }
        else:
            return {
                "role": "system",
                "content": """당신은 대한민국 가정법원에 제출하는 정식 소장(訴狀)을 작성하는 전문 법률가입니다.

[핵심 원칙 - 반드시 준수]
1. 모든 사실관계, 날짜, 발언 내용은 오직 제공된 "증거 자료"에서만 추출하세요
2. 증거에 없는 내용을 임의로 생성하거나 추측하지 마세요
3. 확인되지 않은 정보는 "확인 필요" 또는 "[미확인]"으로 표시하세요

[출력 형식]
- 마크다운, 구분선(===, ---) 사용 금지
- 섹션 간 빈 줄 2개로 구분
- 들여쓰기는 공백 4칸

[소장 구조]
1. 소장 제목
2. 당사자 표시 (원고/피고)
3. 청구취지
4. 청구원인
   - 당사자들의 관계
   - 혼인생활의 경과 (증거 기반)
   - 이혼 사유 (민법 제840조 인용, 증거에서 구체적 사실 인용)
   - 위자료 청구 (근거 명시)
5. 입증방법 (증거 목록)
6. 첨부서류
7. 작성일, 원고 서명, 법원 표시

[증거 인용 방식]
- 각 주장에 [갑 제N호증] 형식으로 증거 번호 명시
- 증거의 원문을 직접 인용: "피고는 '...'라고 발언하였다" [갑 제1호증]
- 날짜, 시간, 발언 내용은 증거에서 그대로 가져올 것

[금액 산정]
- 위자료: 증거에서 확인된 유책행위 정도 기반
- 지연손해금: 연 12% (소송촉진법 제3조)

※ AI 생성 초안이며 변호사 검토 필수
"""
            }

    def _build_user_message(
        self,
        case: Any,
        sections: List[str],
        evidence_context_str: str,
        legal_context_str: str,
        language: str,
        style: str,
        use_json_output: bool
    ) -> dict:
        """
        Build user message with case info and RAG context.

        Args:
            case: Case object
            sections: Sections to generate
            evidence_context_str: Formatted evidence context
            legal_context_str: Formatted legal context
            language: Language code
            style: Writing style
            use_json_output: Whether to request JSON output

        Returns:
            User message dict for GPT-4o
        """
        if use_json_output:
            return {
                "role": "user",
                "content": f"""다음 정보를 바탕으로 이혼 소송 소장 초안을 JSON 형식으로 작성해 주세요.

**사건 정보:**
- 사건명: {case.title}
- 사건 설명: {case.description or "N/A"}

**생성할 섹션:**
{", ".join(sections)}

**관련 법률 조문:**
{legal_context_str}

**증거 자료:**
{evidence_context_str}

**요청사항:**
- 언어: {language}
- 스타일: {style}
- 위 법률 조문과 증거를 기반으로 법률적 논리를 구성해 주세요
- 이혼 사유는 반드시 민법 제840조를 인용하여 작성하세요
- 각 주장에 대해 evidence_refs 배열에 증거 번호를 포함해 주세요

위 스키마에 맞는 JSON을 출력하세요. JSON 외의 텍스트는 출력하지 마세요.
"""
            }
        else:
            return {
                "role": "user",
                "content": f"""다음 정보를 바탕으로 이혼 소송 소장 초안을 작성해 주세요.

**사건 정보:**
- 사건명: {case.title}
- 사건 설명: {case.description or "N/A"}

**생성할 섹션:**
{", ".join(sections)}

**관련 법률 조문:**
{legal_context_str}

**증거 자료:**
{evidence_context_str}

**요청사항:**
- 언어: {language}
- 스타일: {style}
- 위 법률 조문과 증거를 기반으로 법률적 논리를 구성해 주세요
- 이혼 사유는 반드시 민법 제840조를 인용하여 작성하세요
- 각 주장에 대해 증거 번호를 명시해 주세요 (예: [갑 제1호증], [갑 제2호증])

소장 초안을 작성해 주세요.
"""
            }


# Singleton instance for convenience
_prompt_builder = None


def get_prompt_builder() -> PromptBuilder:
    """Get or create PromptBuilder singleton instance."""
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = PromptBuilder()
    return _prompt_builder
