"""
LawUrlGenerator - 국가법령정보센터 법령한글주소 URL 생성기

법령명/사건명/조약명 + 번호 + 날짜로 유효한 국가법령정보센터 딥링크(URL)를 생성합니다.

참고: law-hangul-address-spec.md
"""

from typing import Optional
from urllib.parse import quote


class LawUrlGenerator:
    """국가법령정보센터 법령한글주소 URL 생성기"""

    BASE_URL = "https://www.law.go.kr"

    # 카테고리 코드 → 한글 Prefix 매핑
    PREFIX_MAP = {
        # P0 - 최우선
        "STATUTE": "/법령",
        "CASE_SUPREME": "/판례",

        # P1
        "CASE_CONST": "/헌재결정례",
        "CASE_INTERPRET": "/법령해석례",

        # P2
        "ADMIN_RULE": "/행정규칙",
        "LOCAL_LAW": "/자치법규",

        # 기타
        "STATUTE_EN": "/영문법령",
        "SCHOOL_CORP": "/학칙공단",
        "TREATY": "/조약",
        "CASE_ADMIN_APPEAL": "/행정심판례",
        "FORM_STATUTE": "/법령별표서식",
        "FORM_ADMIN_RULE": "/행정규칙별표서식",
        "FORM_LOCAL": "/자치법규별표서식",
        "SYSTEM_MAP": "/법령체계도",
        "TERM": "/용어",
        "CENTRAL_INTERP": "/중앙부처1차해석",
        "TAX_TRIBUNAL": "/조세심판재결례",
        "IP_TRIBUNAL": "/특허심판재결례",
        "MARINE_SAFETY_TR": "/해양안전심판재결례",
        "ACRC_TR": "/국민권익위원회심판재결례",
        "MPSS_TR": "/인사혁신처소청심사위원회심판재결례",
    }

    # 지원되는 서브카테고리
    SUBCATEGORIES = {
        "AMENDMENT_DOC": "제개정문",
        "OLD_NEW_COMPARE": "신구법비교",
        "THREE_COMPARE": "삼단비교",
        "SUPPLEMENT": "부칙",
        "ARTICLE": None,  # 조문은 sub_item으로 직접 처리
    }

    def __init__(self):
        """URL 생성기 초기화"""
        pass

    @staticmethod
    def _url_segment(s: str) -> str:
        """경로 segment URL 인코딩"""
        return quote(s, safe="")

    @staticmethod
    def _build_bracket(*parts: Optional[str]) -> str:
        """
        빈값 제외 후 콤마로 연결하여 괄호 문자열 생성

        Args:
            *parts: 괄호 안에 들어갈 값들

        Returns:
            "/({인코딩된_값들})" 형식의 문자열. 빈 경우 ""
        """
        vals = [p for p in parts if p]
        if not vals:
            return ""
        inner = ",".join(vals)
        return f"/({LawUrlGenerator._url_segment(inner)})"

    def generate_url(
        self,
        category_code: str,
        title: Optional[str] = None,
        identifier: Optional[str] = None,
        date_val: Optional[str] = None,
        enforce_date: Optional[str] = None,
        sub_item: Optional[str] = None,
        subcategory: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> str:
        """
        국가법령정보센터 법령한글주소 URL 생성

        Args:
            category_code: 카테고리 코드 (STATUTE, CASE_SUPREME, CASE_CONST 등)
            title: 법령명, 판례명, 사건명, 안건명, 조약명 등
            identifier: 공포번호, 발령번호, 사건번호, 안건번호, 조약번호 등
            date_val: 날짜 (YYYYMMDD) - 공포일, 판결일, 의결일, 해석일 등
            enforce_date: 시행일자 (YYYYMMDD) - 법령 시행기준 링크에 사용
            sub_item: 조문/부칙/별표/서식 (제3조, 부칙, 별표28의2 등)
            subcategory: 세부 분류 (AMENDMENT_DOC, OLD_NEW_COMPARE 등)
            org_name: 위원회명 (COMMITTEE_* 카테고리에서 사용)

        Returns:
            생성된 URL 문자열

        Raises:
            ValueError: 필수 파라미터 누락 또는 잘못된 카테고리
        """
        # 1) Prefix 결정
        if category_code.startswith("COMMITTEE_"):
            if not org_name:
                raise ValueError(f"COMMITTEE 카테고리는 org_name이 필수입니다: {category_code}")
            prefix = "/" + org_name
        else:
            prefix = self.PREFIX_MAP.get(category_code)
            if not prefix:
                raise ValueError(f"지원하지 않는 카테고리 코드: {category_code}")

        path = prefix

        # 2) 서브카테고리 (제개정문, 신구법비교 등) 반영
        if category_code == "STATUTE" and subcategory:
            if subcategory == "AMENDMENT_DOC":
                path += "/제개정문"
            elif subcategory == "OLD_NEW_COMPARE":
                path += "/신구법비교"
            elif subcategory == "THREE_COMPARE":
                path += "/삼단비교"
            # ARTICLE, SUPPLEMENT는 sub_item으로 처리

        # 3) SYSTEM_MAP 처리 (법령체계도)
        if category_code == "SYSTEM_MAP":
            if not subcategory:
                raise ValueError("SYSTEM_MAP 카테고리는 subcategory(법령, 판례 등)가 필수입니다")
            path += f"/{self._url_segment(subcategory)}"

        # 4) Title / Term / Case name 추가
        # (별표/서식 카테고리는 title을 괄호 내에서 처리)
        if title and category_code not in {"FORM_STATUTE", "FORM_ADMIN_RULE", "FORM_LOCAL"}:
            path += f"/{self._url_segment(title)}"

        # 5) sub_item (조문/부칙) 처리 - STATUTE 카테고리
        if category_code == "STATUTE" and sub_item:
            path += f"/{self._url_segment(sub_item)}"

        # 6) 괄호 파라미터 조합 (카테고리별 규칙)
        bracket = self._build_bracket_params(
            category_code, identifier, date_val, enforce_date, title
        )

        path += bracket

        return self.BASE_URL + path

    def _build_bracket_params(
        self,
        category_code: str,
        identifier: Optional[str],
        date_val: Optional[str],
        enforce_date: Optional[str],
        title: Optional[str],
    ) -> str:
        """
        카테고리별 괄호 파라미터 생성

        Args:
            category_code: 카테고리 코드
            identifier: 식별자 (번호)
            date_val: 날짜
            enforce_date: 시행일
            title: 제목 (별표/서식용)

        Returns:
            괄호 파라미터 문자열
        """
        if category_code == "STATUTE":
            # 법령: (enforce_date?, identifier?, date_val?)
            return self._build_bracket(enforce_date, identifier, date_val)

        elif category_code in {"ADMIN_RULE", "LOCAL_LAW", "SCHOOL_CORP", "TREATY", "STATUTE_EN"}:
            # (identifier, date_val) 조합
            return self._build_bracket(identifier, date_val)

        elif category_code in {
            "CASE_SUPREME",
            "CASE_CONST",
            "CASE_INTERPRET",
            "CASE_ADMIN_APPEAL",
            "TAX_TRIBUNAL",
            "IP_TRIBUNAL",
            "MARINE_SAFETY_TR",
            "ACRC_TR",
            "MPSS_TR",
        }:
            # 판례/결정례: (identifier, date_val?) - 날짜 생략 가능
            return self._build_bracket(identifier, date_val)

        elif category_code == "CENTRAL_INTERP":
            # 중앙부처1차해석: (identifier, date_val?)
            return self._build_bracket(identifier, date_val)

        elif category_code in {"FORM_STATUTE", "FORM_ADMIN_RULE", "FORM_LOCAL"}:
            # 별표/서식: (title, identifier)
            return self._build_bracket(title, identifier)

        elif category_code.startswith("COMMITTEE_"):
            # 위원회: (identifier, date_val?)
            return self._build_bracket(identifier, date_val)

        return ""

    # --- 편의 메서드: 자주 사용되는 패턴 ---

    def generate_statute_url(
        self,
        title: str,
        article: Optional[str] = None,
        identifier: Optional[str] = None,
        date_val: Optional[str] = None,
        enforce_date: Optional[str] = None,
    ) -> str:
        """
        법령 URL 생성 (P0)

        Args:
            title: 법령명 (예: "민법", "자동차관리법")
            article: 조문 (예: "제840조", "제3조")
            identifier: 공포번호
            date_val: 공포일자 (YYYYMMDD)
            enforce_date: 시행일자 (YYYYMMDD)

        Returns:
            법령 URL

        Examples:
            >>> gen = LawUrlGenerator()
            >>> gen.generate_statute_url("민법")
            'https://www.law.go.kr/법령/민법'
            >>> gen.generate_statute_url("민법", article="제840조")
            'https://www.law.go.kr/법령/민법/제840조'
        """
        return self.generate_url(
            category_code="STATUTE",
            title=title,
            sub_item=article,
            identifier=identifier,
            date_val=date_val,
            enforce_date=enforce_date,
        )

    def generate_case_url(
        self,
        case_number: str,
        title: Optional[str] = None,
        date_val: Optional[str] = None,
    ) -> str:
        """
        대법원 판례 URL 생성 (P0)

        Args:
            case_number: 사건번호 (예: "2013다214529")
            title: 판례명 (선택)
            date_val: 판결일자 (YYYYMMDD)

        Returns:
            판례 URL

        Examples:
            >>> gen = LawUrlGenerator()
            >>> gen.generate_case_url("2013다214529")
            'https://www.law.go.kr/판례/(2013다214529)'
        """
        return self.generate_url(
            category_code="CASE_SUPREME",
            title=title,
            identifier=case_number,
            date_val=date_val,
        )

    def generate_constitutional_case_url(
        self,
        case_number: str,
        title: Optional[str] = None,
        date_val: Optional[str] = None,
    ) -> str:
        """
        헌법재판소 결정례 URL 생성 (P1)

        Args:
            case_number: 사건번호 (예: "2018헌바26")
            title: 사건명 (선택)
            date_val: 선고일자 (YYYYMMDD)

        Returns:
            헌재결정례 URL
        """
        return self.generate_url(
            category_code="CASE_CONST",
            title=title,
            identifier=case_number,
            date_val=date_val,
        )

    def generate_interpretation_url(
        self,
        case_number: str,
        title: Optional[str] = None,
        date_val: Optional[str] = None,
    ) -> str:
        """
        법령해석례 URL 생성 (P1)

        Args:
            case_number: 사건번호
            title: 제목 (선택)
            date_val: 해석일자 (YYYYMMDD)

        Returns:
            법령해석례 URL
        """
        return self.generate_url(
            category_code="CASE_INTERPRET",
            title=title,
            identifier=case_number,
            date_val=date_val,
        )


# 모듈 레벨 편의 함수
def generate_law_url(
    category_code: str,
    title: Optional[str] = None,
    identifier: Optional[str] = None,
    date_val: Optional[str] = None,
    enforce_date: Optional[str] = None,
    sub_item: Optional[str] = None,
    subcategory: Optional[str] = None,
    org_name: Optional[str] = None,
) -> str:
    """
    국가법령정보센터 법령한글주소 URL 생성 (편의 함수)

    LawUrlGenerator().generate_url()의 래퍼 함수
    """
    generator = LawUrlGenerator()
    return generator.generate_url(
        category_code=category_code,
        title=title,
        identifier=identifier,
        date_val=date_val,
        enforce_date=enforce_date,
        sub_item=sub_item,
        subcategory=subcategory,
        org_name=org_name,
    )
