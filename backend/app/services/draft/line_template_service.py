"""
Line Template Service - Handles line-based template processing
Extracted from DraftService for better modularity (Issue #325)
"""

from typing import List, Any
from datetime import datetime, timezone
import re
import copy

from app.utils.qdrant import get_template_by_type, search_evidence_by_semantic
from app.utils.dynamo import get_evidence_by_case
from app.utils.openai_client import generate_chat_completion
from app.middleware import NotFoundError


class LineTemplateService:
    """
    Handles line-based template loading, placeholder filling, and rendering.
    """

    def __init__(self, rag_orchestrator=None, prompt_builder=None):
        """
        Initialize line template service

        Args:
            rag_orchestrator: Optional RAGOrchestrator for context formatting
            prompt_builder: Optional PromptBuilder for AI content generation
        """
        self.rag_orchestrator = rag_orchestrator
        self.prompt_builder = prompt_builder

    def load_template(self, template_type: str) -> dict:
        """
        Load line-based template from Qdrant

        Args:
            template_type: Template type (e.g., "이혼소장")

        Returns:
            Template dict with lines array

        Raises:
            NotFoundError: Template not found
        """
        template = get_template_by_type(template_type)
        if not template:
            raise NotFoundError(f"Template '{template_type}' not found")
        return template

    def fill_placeholders(
        self,
        template_lines: List[dict],
        case_data: dict
    ) -> List[dict]:
        """
        Fill placeholders in template lines with case data

        Placeholders use {{placeholder_key}} format.
        Supports multiple placeholders per line.

        Args:
            template_lines: List of line dicts from template
            case_data: Dict mapping placeholder keys to values

        Returns:
            New list of lines with placeholders replaced
        """
        filled_lines = []
        for line in template_lines:
            new_line = copy.deepcopy(line)
            text = new_line.get("text", "")

            # Find all {{placeholder}} patterns
            placeholders = re.findall(r'\{\{([^}]+)\}\}', text)

            for placeholder in placeholders:
                # Try placeholder_key first, then Korean text
                value = case_data.get(
                    line.get("placeholder_key", ""),
                    case_data.get(placeholder, "")
                )

                if value:
                    text = text.replace(f"{{{{{placeholder}}}}}", str(value))
                elif not value and not case_data:
                    # Keep placeholder or mark as empty
                    text = text.replace(f"{{{{{placeholder}}}}}", "[미입력]")

            new_line["text"] = text
            filled_lines.append(new_line)

        return filled_lines

    def filter_conditional_lines(
        self,
        template_lines: List[dict],
        case_conditions: dict
    ) -> List[dict]:
        """
        Filter template lines based on conditions

        Lines with 'condition' field are only included if the
        corresponding condition in case_conditions is True.
        Lines without 'condition' field are always included.

        Args:
            template_lines: List of line dicts from template
            case_conditions: Dict mapping condition names to booleans

        Returns:
            Filtered list of lines
        """
        filtered = []
        for line in template_lines:
            condition = line.get("condition")
            if condition is None:
                # No condition - always include
                filtered.append(line)
            elif case_conditions.get(condition, False):
                # Condition exists and is True
                filtered.append(line)
            # else: condition is False, skip line

        return filtered

    def fill_ai_generated_content(
        self,
        template_lines: List[dict],
        evidence_context: List[dict],
        case_id: str
    ) -> List[dict]:
        """
        Generate AI content for placeholders marked as ai_generated

        Only processes lines where ai_generated=True.
        Uses GPT-4o to generate appropriate content based on evidence.

        Args:
            template_lines: List of line dicts
            evidence_context: Evidence data for context
            case_id: Case ID for RAG

        Returns:
            Lines with AI-generated content filled in
        """
        filled_lines = []
        for line in template_lines:
            new_line = copy.deepcopy(line)

            if line.get("ai_generated", False) and line.get("is_placeholder", False):
                placeholder_key = line.get("placeholder_key", "")
                section = line.get("section", "general")

                # Build prompt for this specific placeholder
                if self.prompt_builder:
                    prompt = self.prompt_builder.build_ai_placeholder_prompt(
                        placeholder_key,
                        section,
                        evidence_context
                    )
                else:
                    prompt = self._build_ai_placeholder_prompt(
                        placeholder_key,
                        section,
                        evidence_context
                    )

                # Generate content using gpt-4o-mini for faster response
                ai_content = generate_chat_completion(prompt, model="gpt-4o-mini")
                new_line["text"] = ai_content

            filled_lines.append(new_line)

        return filled_lines

    def _build_ai_placeholder_prompt(
        self,
        placeholder_key: str,
        section: str,
        evidence_context: List[dict]
    ) -> List[dict]:
        """Build prompt for AI placeholder generation (fallback)"""
        evidence_text = self._format_evidence_context(evidence_context)

        system_prompt = """당신은 한국 가정법 전문 법률가입니다.
소장의 특정 부분을 작성해야 합니다.
증거 자료를 바탕으로 법적으로 정확하고 간결한 내용을 작성하세요.
- 증거를 인용할 때는 "갑 제N호증"으로 표기
- 민법 제840조 이혼 사유에 맞는 법률 용어 사용
- 문장은 완결형으로, 불필요한 수식어 제외"""

        section_guides = {
            "청구취지_내용": "청구취지를 작성하세요. 원고가 피고에게 요청하는 사항을 명확히 기재.",
            "청구원인_내용": "청구원인을 작성하세요. 이혼 사유와 그 근거를 증거와 함께 서술.",
            "grounds_content": "청구원인의 핵심 내용을 작성하세요.",
            "claims_content": "청구취지의 핵심 내용을 작성하세요."
        }

        guide = section_guides.get(placeholder_key, f"{placeholder_key} 내용을 작성하세요.")

        user_prompt = f"""## 작성 대상
{guide}

## 증거 자료
{evidence_text}

## 지침
- 증거에 기반한 사실만 기술
- 간결하고 법적으로 정확하게 작성
- 2-3문장 이내로 작성"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def _format_evidence_context(self, evidence_results: List[dict]) -> str:
        """Format evidence context for prompt (fallback)"""
        if not evidence_results:
            return "(증거 자료 없음)"

        parts = []
        for i, doc in enumerate(evidence_results, 1):
            content = doc.get("document") or doc.get("content", "")
            if len(content) > 500:
                content = content[:500] + "..."
            parts.append(f"[갑 제{i}호증]\n{content}")
        return "\n\n".join(parts)

    def render_to_text(self, lines: List[dict]) -> str:
        """
        Render line-based JSON to formatted plain text

        Applies indentation and spacing from format info.

        Args:
            lines: List of line dicts with format info

        Returns:
            Formatted text string
        """
        output_lines = []

        for line in lines:
            text = line.get("text", "")
            fmt = line.get("format", {})

            # Apply indentation
            indent = fmt.get("indent", 0)
            if indent > 0:
                text = " " * indent + text

            output_lines.append(text)

            # Apply spacing after
            spacing_after = fmt.get("spacing_after", 0)
            for _ in range(spacing_after):
                output_lines.append("")

        return "\n".join(output_lines)

    def generate_draft(
        self,
        case_id: str,
        case: Any,
        case_data: dict,
        template_type: str = "이혼소장"
    ) -> dict:
        """
        Generate draft using line-based template

        Full pipeline:
        1. Load template from Qdrant
        2. Filter conditional lines
        3. Fill static placeholders
        4. Generate AI content for ai_generated placeholders
        5. Return structured result

        Args:
            case_id: Case ID
            case: Case object
            case_data: Data for placeholders
            template_type: Template type to use

        Returns:
            Dict with lines and metadata
        """
        # 1. Load template
        template = self.load_template(template_type)
        lines = template.get("lines", [])

        # 2. Determine conditions from case data
        case_conditions = {
            "has_children": case_data.get("has_children", False),
            "has_alimony": case_data.get("has_alimony", False),
            "has_property": case_data.get("has_property", False)
        }

        # 3. Filter conditional lines
        lines = self.filter_conditional_lines(lines, case_conditions)

        # 4. Fill static placeholders
        lines = self.fill_placeholders(lines, case_data)

        # 5. Get evidence for AI generation
        evidence = get_evidence_by_case(case_id)
        done_evidence = [e for e in evidence if e.get("status") == "done"]

        # 6. Fill AI-generated content
        if done_evidence:
            rag_results = search_evidence_by_semantic(
                case_id=case_id,
                query="이혼 귀책사유 증거",
                top_k=5
            )
            lines = self.fill_ai_generated_content(lines, rag_results, case_id)

        return {
            "case_id": case_id,
            "template_type": template_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "lines": lines
        }
