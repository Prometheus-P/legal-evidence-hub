"""
DocumentRenderer - JSON 법률 문서를 포맷팅된 텍스트로 변환

JSON 스키마의 format 객체를 해석하여 적절한 들여쓰기, 정렬, 줄간격을 적용합니다.
"""

import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class DocumentRenderer:
    """
    JSON 법률 문서를 포맷팅된 텍스트로 렌더링

    Usage:
        renderer = DocumentRenderer()
        text = renderer.render_to_text(json_doc)
    """

    # 기본 문서 너비 (칸)
    DEFAULT_WIDTH = 80

    # 기본 들여쓰기 칸 수
    INDENT_CHARS = 4

    def __init__(self, width: int = DEFAULT_WIDTH):
        """
        Args:
            width: 문서 너비 (칸)
        """
        self.width = width

    def render_to_text(self, doc: Dict[str, Any]) -> str:
        """
        JSON 문서를 포맷팅된 텍스트로 변환

        Args:
            doc: JSON 문서 딕셔너리

        Returns:
            포맷팅된 텍스트 문자열
        """
        if not doc:
            return ""

        lines = []

        try:
            # 1. Header (소장 제목)
            if "header" in doc:
                lines.extend(self._render_header(doc["header"]))

            # 2. Parties (당사자 표시)
            if "parties" in doc:
                lines.extend(self._render_parties(doc["parties"]))

            # 3. Claims (청구취지)
            if "claims" in doc:
                lines.extend(self._render_claims(doc["claims"]))

            # 4. Grounds (청구원인)
            if "grounds" in doc:
                lines.extend(self._render_grounds(doc["grounds"]))

            # 5. Evidence (입증방법)
            if "evidence" in doc:
                lines.extend(self._render_evidence(doc["evidence"]))

            # 6. Attachments (첨부서류)
            if "attachments" in doc:
                lines.extend(self._render_attachments(doc["attachments"]))

            # 7. Footer (작성일, 서명, 법원)
            if "footer" in doc:
                lines.extend(self._render_footer(doc["footer"]))

        except Exception as e:
            logger.error(f"Error rendering document: {e}")
            # Fallback: JSON을 그대로 반환
            return json.dumps(doc, ensure_ascii=False, indent=2)

        return "\n".join(lines)

    def _apply_format(
        self,
        text: str,
        fmt: Optional[Dict[str, Any]] = None
    ) -> str:
        """포맷 객체를 적용하여 텍스트 변환"""
        if not fmt:
            return text

        result = text

        # 들여쓰기
        indent_level = fmt.get("indent_level", 0)
        if indent_level > 0:
            indent = " " * (indent_level * self.INDENT_CHARS)
            result = indent + result

        # 정렬
        alignment = fmt.get("alignment", "left")
        if alignment == "center":
            result = result.center(self.width)
        elif alignment == "right":
            result = result.rjust(self.width)

        return result

    def _add_spacing(self, lines: List[str], fmt: Optional[Dict[str, Any]] = None) -> None:
        """줄간격 추가"""
        if not fmt:
            return

        spacing_after = fmt.get("spacing_after", 0)
        for _ in range(spacing_after):
            lines.append("")

    def _render_header(self, header: Dict[str, Any]) -> List[str]:
        """헤더 렌더링"""
        lines = []

        # 제목
        if "title" in header:
            title_obj = header["title"]
            text = title_obj.get("text", "소    장")
            fmt = title_obj.get("format", {})
            lines.append(self._apply_format(text, fmt))
            self._add_spacing(lines, fmt)

        # 사건번호
        if "case_number" in header:
            case_obj = header["case_number"]
            text = case_obj.get("text", "")
            if text:
                fmt = case_obj.get("format", {})
                lines.append(self._apply_format(text, fmt))
                self._add_spacing(lines, fmt)

        return lines

    def _render_parties(self, parties: Dict[str, Any]) -> List[str]:
        """당사자 표시 렌더링"""
        lines = []
        party_format = parties.get("format", {})
        label_width = party_format.get("label_width", 10)

        # 원고
        if "plaintiff" in parties:
            p = parties["plaintiff"]
            label = p.get("label", "원    고")
            name = p.get("name", "")
            lines.append(f"{label.ljust(label_width)} {name}")

            if p.get("resident_number"):
                lines.append(f"{' ' * label_width} 주민등록번호: {p['resident_number']}")
            if p.get("address"):
                lines.append(f"{' ' * label_width} 주소: {p['address']}")
            if p.get("registered_address"):
                lines.append(f"{' ' * label_width} 등록기준지: {p['registered_address']}")
            if p.get("contact"):
                lines.append(f"{' ' * label_width} 연락처: {p['contact']}")

        lines.append("")

        # 피고
        if "defendant" in parties:
            d = parties["defendant"]
            label = d.get("label", "피    고")
            name = d.get("name", "")
            lines.append(f"{label.ljust(label_width)} {name}")

            if d.get("resident_number"):
                lines.append(f"{' ' * label_width} 주민등록번호: {d['resident_number']}")
            if d.get("address"):
                lines.append(f"{' ' * label_width} 주소: {d['address']}")
            if d.get("registered_address"):
                lines.append(f"{' ' * label_width} 등록기준지: {d['registered_address']}")

        lines.append("")
        lines.append("")

        return lines

    def _render_claims(self, claims: Dict[str, Any]) -> List[str]:
        """청구취지 렌더링"""
        lines = []

        # 섹션 제목
        title_obj = claims.get("title", {})
        title_text = title_obj.get("text", "청 구 취 지")
        title_fmt = title_obj.get("format", {})
        lines.append(self._apply_format(title_text, title_fmt))
        self._add_spacing(lines, title_fmt)

        # 청구 항목들
        items = claims.get("items", [])
        for i, item in enumerate(items, 1):
            text = item.get("text", "")
            fmt = item.get("format", {"indent_level": 1})

            # 번호 붙이기
            numbered_text = f"{i}. {text}"
            lines.append(self._apply_format(numbered_text, fmt))

        lines.append("")
        lines.append("라는 판결을 구합니다.")
        lines.append("")
        lines.append("")

        return lines

    def _render_grounds(self, grounds: Dict[str, Any]) -> List[str]:
        """청구원인 렌더링"""
        lines = []

        # 섹션 제목
        title_obj = grounds.get("title", {})
        title_text = title_obj.get("text", "청 구 원 인")
        title_fmt = title_obj.get("format", {})
        lines.append(self._apply_format(title_text, title_fmt))
        self._add_spacing(lines, title_fmt)

        # 섹션들
        sections = grounds.get("sections", [])
        for section in sections:
            # 섹션 제목
            section_title = section.get("title", {})
            s_text = section_title.get("text", "")
            s_fmt = section_title.get("format", {})
            if s_text:
                lines.append(self._apply_format(s_text, s_fmt))
                self._add_spacing(lines, s_fmt)

            # 문단들
            paragraphs = section.get("paragraphs", [])
            for para in paragraphs:
                p_text = para.get("text", "")
                p_fmt = para.get("format", {"indent_level": 1})

                # 증거 참조 추가
                evidence_refs = para.get("evidence_refs", [])
                if evidence_refs:
                    p_text += f" [{', '.join(evidence_refs)}]"

                lines.append(self._apply_format(p_text, p_fmt))
                self._add_spacing(lines, p_fmt)

            # 법적 근거
            legal_basis = section.get("legal_basis", {})
            if legal_basis:
                statute = legal_basis.get("statute", "")
                article = legal_basis.get("article", "")
                content = legal_basis.get("content", "")
                if statute and article:
                    lines.append("")
                    lines.append(self._apply_format(f"[{statute} {article}]", {"indent_level": 1}))
                    if content:
                        lines.append(self._apply_format(content, {"indent_level": 1}))
                    lines.append("")

            lines.append("")

        return lines

    def _render_evidence(self, evidence: Dict[str, Any]) -> List[str]:
        """입증방법 렌더링"""
        lines = []

        # 섹션 제목
        title_obj = evidence.get("title", {})
        title_text = title_obj.get("text", "입 증 방 법")
        title_fmt = title_obj.get("format", {})
        lines.append(self._apply_format(title_text, title_fmt))
        self._add_spacing(lines, title_fmt)

        # 증거 목록
        items = evidence.get("items", [])
        for item in items:
            number = item.get("number", "")
            description = item.get("description", "")
            text = f"{number}  {description}"
            fmt = item.get("format", {"indent_level": 1})
            lines.append(self._apply_format(text, fmt))

        lines.append("")
        lines.append("")

        return lines

    def _render_attachments(self, attachments: Dict[str, Any]) -> List[str]:
        """첨부서류 렌더링"""
        lines = []

        # 섹션 제목
        title_obj = attachments.get("title", {})
        title_text = title_obj.get("text", "첨 부 서 류")
        title_fmt = title_obj.get("format", {})
        lines.append(self._apply_format(title_text, title_fmt))
        self._add_spacing(lines, title_fmt)

        # 첨부 목록
        items = attachments.get("items", [])
        for i, item in enumerate(items, 1):
            text = item.get("text", "")
            copies = item.get("copies", 1)
            fmt = item.get("format", {"indent_level": 1})
            numbered_text = f"{i}. {text}"
            if copies > 1:
                numbered_text += f"  {copies}통"
            else:
                numbered_text += "  1통"
            lines.append(self._apply_format(numbered_text, fmt))

        lines.append("")
        lines.append("")

        return lines

    def _render_footer(self, footer: Dict[str, Any]) -> List[str]:
        """푸터 렌더링 (날짜, 서명, 법원)"""
        lines = []

        # 날짜
        if "date" in footer:
            date_obj = footer["date"]
            text = date_obj.get("text", "")
            fmt = date_obj.get("format", {"alignment": "center"})
            lines.append(self._apply_format(text, fmt))
            self._add_spacing(lines, fmt)

        lines.append("")

        # 원고 서명
        if "signature" in footer:
            sig_obj = footer["signature"]
            # 원고 이름
            name = sig_obj.get("plaintiff_name", "")
            fmt = sig_obj.get("format", {"alignment": "right"})
            if name:
                lines.append(self._apply_format(f"원고  {name}  (서명 또는 날인)", fmt))

        lines.append("")
        lines.append("")

        # 법원
        if "court" in footer:
            court_obj = footer["court"]
            text = court_obj.get("text", "")
            fmt = court_obj.get("format", {"alignment": "center"})
            if text:
                lines.append(self._apply_format(f"{text} 귀중", fmt))

        return lines

    def parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        GPT 응답에서 JSON 추출 및 파싱

        Args:
            response_text: GPT 응답 텍스트

        Returns:
            파싱된 JSON 딕셔너리, 실패 시 None
        """
        try:
            # 먼저 전체가 JSON인지 시도
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # JSON 블록 추출 시도 (```json ... ```)
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # { 로 시작하는 JSON 객체 추출 시도
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("Failed to parse JSON from response")
        return None

    # ==========================================================================
    # Line-Based Template Rendering (Phase: 라인별 JSON 템플릿)
    # ==========================================================================

    def render_line_based(self, lines: List[Dict[str, Any]]) -> str:
        """
        라인 기반 JSON 템플릿을 포맷팅된 텍스트로 렌더링

        각 라인의 format 정보를 적용하여 정확한 레이아웃 생성

        Args:
            lines: 라인 딕셔너리 리스트 (line, text, format 포함)

        Returns:
            포맷팅된 텍스트 문자열

        Example:
            lines = [
                {"line": 1, "text": "소장", "format": {"align": "center", "bold": True}},
                {"line": 2, "text": "", "format": {"spacing_after": 1}},
                {"line": 3, "text": "원고: 김영희", "format": {"indent": 0}}
            ]
            renderer.render_line_based(lines)
        """
        output_lines = []

        for line in lines:
            text = line.get("text", "")
            fmt = line.get("format", {})

            # 들여쓰기 적용
            indent = fmt.get("indent", 0)
            if indent > 0:
                text = " " * indent + text

            # 정렬 적용
            align = fmt.get("align", "left")
            if align == "center":
                text = text.center(self.width)
            elif align == "right":
                text = text.rjust(self.width)

            output_lines.append(text)

            # 줄간격 적용
            spacing_after = fmt.get("spacing_after", 0)
            for _ in range(spacing_after):
                output_lines.append("")

        return "\n".join(output_lines)

    def render_line_based_sections(
        self,
        lines: List[Dict[str, Any]],
        section_filter: Optional[str] = None
    ) -> str:
        """
        특정 섹션만 필터링하여 렌더링

        Args:
            lines: 라인 딕셔너리 리스트
            section_filter: 렌더링할 섹션 이름 (None이면 전체)

        Returns:
            필터링된 포맷팅 텍스트
        """
        if section_filter:
            filtered = [line for line in lines if line.get("section") == section_filter]
        else:
            filtered = lines

        return self.render_line_based(filtered)

    def lines_to_html(self, lines: List[Dict[str, Any]]) -> str:
        """
        라인 기반 JSON을 HTML로 변환 (미리보기용)

        Args:
            lines: 라인 딕셔너리 리스트

        Returns:
            HTML 문자열
        """
        html_parts = ['<div class="document-preview">']

        for line in lines:
            text = line.get("text", "")
            fmt = line.get("format", {})

            # CSS 스타일 구성
            styles = []

            # 정렬
            align = fmt.get("align", "left")
            styles.append(f"text-align: {align}")

            # 들여쓰기
            indent = fmt.get("indent", 0)
            if indent > 0:
                styles.append(f"padding-left: {indent * 6}px")

            # 굵기
            if fmt.get("bold", False):
                styles.append("font-weight: bold")

            # 글자 크기
            font_size = fmt.get("font_size", 12)
            if font_size != 12:
                styles.append(f"font-size: {font_size}pt")

            # 줄간격
            spacing_after = fmt.get("spacing_after", 0)
            if spacing_after > 0:
                styles.append(f"margin-bottom: {spacing_after * 12}px")

            style_str = "; ".join(styles)

            # 빈 줄 처리
            if not text:
                html_parts.append(f'<p style="{style_str}">&nbsp;</p>')
            else:
                # HTML 이스케이프
                import html
                safe_text = html.escape(text)
                html_parts.append(f'<p style="{style_str}">{safe_text}</p>')

        html_parts.append('</div>')
        return "\n".join(html_parts)
