"""
Unit tests for LawUrlGenerator
국가법령정보센터 법령한글주소 URL 생성기 테스트
"""

import pytest
from urllib.parse import unquote

from app.services.law_url_generator import LawUrlGenerator, generate_law_url


@pytest.fixture
def generator():
    """LawUrlGenerator 인스턴스 생성"""
    return LawUrlGenerator()


class TestStatuteUrls:
    """법령 URL 테스트 (P0)"""

    def test_statute_basic(self, generator):
        """기본 법령 URL"""
        url = generator.generate_url(category_code="STATUTE", title="민법")
        assert "www.law.go.kr" in url
        assert unquote(url) == "https://www.law.go.kr/법령/민법"

    def test_statute_article(self, generator):
        """법령 + 조문 URL"""
        url = generator.generate_url(
            category_code="STATUTE",
            title="민법",
            sub_item="제840조"
        )
        assert unquote(url) == "https://www.law.go.kr/법령/민법/제840조"

    def test_statute_article_with_detail(self, generator):
        """법령 + 세부 조문 URL"""
        url = generator.generate_url(
            category_code="STATUTE",
            title="자동차관리법",
            sub_item="제3조"
        )
        assert unquote(url) == "https://www.law.go.kr/법령/자동차관리법/제3조"

    def test_statute_with_history_identifier(self, generator):
        """법령 연혁 (공포번호) URL"""
        url = generator.generate_url(
            category_code="STATUTE",
            title="민법",
            identifier="17905"
        )
        assert unquote(url) == "https://www.law.go.kr/법령/민법/(17905)"

    def test_statute_with_history_detail(self, generator):
        """법령 연혁 (공포번호+공포일) URL"""
        url = generator.generate_url(
            category_code="STATUTE",
            title="민법",
            identifier="17905",
            date_val="20210121"
        )
        assert unquote(url) == "https://www.law.go.kr/법령/민법/(17905,20210121)"

    def test_statute_with_enforce_date(self, generator):
        """법령 시행일 기준 URL"""
        url = generator.generate_url(
            category_code="STATUTE",
            title="민법",
            enforce_date="20210722",
            identifier="17905",
            date_val="20210121"
        )
        assert unquote(url) == "https://www.law.go.kr/법령/민법/(20210722,17905,20210121)"

    def test_statute_amendment_doc(self, generator):
        """제개정문 URL"""
        url = generator.generate_url(
            category_code="STATUTE",
            title="민법",
            subcategory="AMENDMENT_DOC"
        )
        assert unquote(url) == "https://www.law.go.kr/법령/제개정문/민법"

    def test_statute_old_new_compare(self, generator):
        """신구법비교 URL"""
        url = generator.generate_url(
            category_code="STATUTE",
            title="민법",
            subcategory="OLD_NEW_COMPARE"
        )
        assert unquote(url) == "https://www.law.go.kr/법령/신구법비교/민법"

    def test_statute_supplement(self, generator):
        """부칙 URL"""
        url = generator.generate_url(
            category_code="STATUTE",
            title="민법",
            sub_item="부칙"
        )
        assert unquote(url) == "https://www.law.go.kr/법령/민법/부칙"


class TestCaseSupremeUrls:
    """대법원 판례 URL 테스트 (P0)"""

    def test_case_by_number(self, generator):
        """사건번호 기반 판례 URL"""
        url = generator.generate_url(
            category_code="CASE_SUPREME",
            identifier="2013다214529"
        )
        assert unquote(url) == "https://www.law.go.kr/판례/(2013다214529)"

    def test_case_by_number_and_date(self, generator):
        """사건번호+판결일 판례 URL"""
        url = generator.generate_url(
            category_code="CASE_SUPREME",
            identifier="2013다214529",
            date_val="20140724"
        )
        assert unquote(url) == "https://www.law.go.kr/판례/(2013다214529,20140724)"

    def test_case_with_title(self, generator):
        """판례명 포함 URL"""
        url = generator.generate_url(
            category_code="CASE_SUPREME",
            title="대법원 2014. 7. 24. 선고 2013다214529 판결",
            identifier="2013다214529",
            date_val="20140724"
        )
        # URL에 판례명이 포함되어야 함
        assert "판례" in unquote(url)
        assert "2013다214529" in unquote(url)


class TestConstitutionalCaseUrls:
    """헌재결정례 URL 테스트 (P1)"""

    def test_const_case_by_number(self, generator):
        """사건번호 기반 헌재결정례 URL"""
        url = generator.generate_url(
            category_code="CASE_CONST",
            identifier="2018헌바26"
        )
        assert unquote(url) == "https://www.law.go.kr/헌재결정례/(2018헌바26)"

    def test_const_case_with_title(self, generator):
        """사건명 포함 헌재결정례 URL"""
        url = generator.generate_url(
            category_code="CASE_CONST",
            title="민법 제847조 제1항 위헌소원",
            identifier="2018헌바26"
        )
        assert "헌재결정례" in unquote(url)
        assert "2018헌바26" in unquote(url)


class TestInterpretationUrls:
    """법령해석례 URL 테스트 (P1)"""

    def test_interpret_by_number(self, generator):
        """사건번호 기반 법령해석례 URL"""
        url = generator.generate_url(
            category_code="CASE_INTERPRET",
            identifier="법제처-2020-0001"
        )
        assert unquote(url) == "https://www.law.go.kr/법령해석례/(법제처-2020-0001)"

    def test_interpret_with_title(self, generator):
        """제목 포함 법령해석례 URL"""
        url = generator.generate_url(
            category_code="CASE_INTERPRET",
            title="민법 제840조 해석",
            identifier="법제처-2020-0001"
        )
        assert "법령해석례" in unquote(url)


class TestAdminRuleUrls:
    """행정규칙 URL 테스트 (P2)"""

    def test_admin_rule_basic(self, generator):
        """기본 행정규칙 URL"""
        url = generator.generate_url(
            category_code="ADMIN_RULE",
            title="개인정보 보호지침"
        )
        assert unquote(url) == "https://www.law.go.kr/행정규칙/개인정보 보호지침"

    def test_admin_rule_with_identifier(self, generator):
        """발령번호 포함 행정규칙 URL"""
        url = generator.generate_url(
            category_code="ADMIN_RULE",
            title="개인정보 보호지침",
            identifier="제2020-1호",
            date_val="20200315"
        )
        assert "행정규칙" in unquote(url)
        assert "제2020-1호" in unquote(url)


class TestLocalLawUrls:
    """자치법규 URL 테스트 (P2)"""

    def test_local_law_basic(self, generator):
        """기본 자치법규 URL"""
        url = generator.generate_url(
            category_code="LOCAL_LAW",
            title="서울특별시 주차장 설치 및 관리 조례"
        )
        assert "자치법규" in unquote(url)

    def test_local_law_with_identifier(self, generator):
        """공포번호 포함 자치법규 URL"""
        url = generator.generate_url(
            category_code="LOCAL_LAW",
            title="서울특별시 조례",
            identifier="제7000호",
            date_val="20200101"
        )
        assert "자치법규" in unquote(url)


class TestTreatyUrls:
    """조약 URL 테스트"""

    def test_treaty_basic(self, generator):
        """기본 조약 URL"""
        url = generator.generate_url(
            category_code="TREATY",
            title="대한민국과 일본국 간의 어업에 관한 협정"
        )
        assert "조약" in unquote(url)

    def test_treaty_by_number(self, generator):
        """번호+발효일 조약 URL"""
        url = generator.generate_url(
            category_code="TREATY",
            identifier="제1234호",
            date_val="19980101"
        )
        assert "조약" in unquote(url)


class TestTermUrls:
    """법령용어 URL 테스트"""

    def test_term_basic(self, generator):
        """기본 용어 URL"""
        url = generator.generate_url(
            category_code="TERM",
            title="선박"
        )
        assert unquote(url) == "https://www.law.go.kr/용어/선박"


class TestSystemMapUrls:
    """법령체계도 URL 테스트"""

    def test_system_map_statute(self, generator):
        """법령 체계도 URL"""
        url = generator.generate_url(
            category_code="SYSTEM_MAP",
            title="민법",
            subcategory="법령"
        )
        assert "법령체계도" in unquote(url)
        assert "법령" in unquote(url)
        assert "민법" in unquote(url)

    def test_system_map_case(self, generator):
        """판례 체계도 URL"""
        url = generator.generate_url(
            category_code="SYSTEM_MAP",
            title="소유권",
            subcategory="판례"
        )
        assert "법령체계도" in unquote(url)
        assert "판례" in unquote(url)

    def test_system_map_requires_subcategory(self, generator):
        """SYSTEM_MAP은 subcategory 필수"""
        with pytest.raises(ValueError, match="subcategory"):
            generator.generate_url(
                category_code="SYSTEM_MAP",
                title="민법"
            )


class TestCommitteeUrls:
    """위원회 결정 URL 테스트"""

    def test_committee_url(self, generator):
        """위원회 결정 URL"""
        url = generator.generate_url(
            category_code="COMMITTEE_PIPC",
            org_name="개인정보보호위원회",
            title="개인정보 처리 위반 결정",
            identifier="2020-123"
        )
        assert "개인정보보호위원회" in unquote(url)
        assert "2020-123" in unquote(url)

    def test_committee_requires_org_name(self, generator):
        """COMMITTEE 카테고리는 org_name 필수"""
        with pytest.raises(ValueError, match="org_name"):
            generator.generate_url(
                category_code="COMMITTEE_FTC",
                title="공정거래 위반 결정"
            )


class TestConvenienceMethods:
    """편의 메서드 테스트"""

    def test_generate_statute_url(self, generator):
        """generate_statute_url 편의 메서드"""
        url = generator.generate_statute_url("민법")
        assert unquote(url) == "https://www.law.go.kr/법령/민법"

    def test_generate_statute_url_with_article(self, generator):
        """generate_statute_url with article"""
        url = generator.generate_statute_url("민법", article="제840조")
        assert unquote(url) == "https://www.law.go.kr/법령/민법/제840조"

    def test_generate_case_url(self, generator):
        """generate_case_url 편의 메서드"""
        url = generator.generate_case_url("2013다214529")
        assert unquote(url) == "https://www.law.go.kr/판례/(2013다214529)"

    def test_generate_constitutional_case_url(self, generator):
        """generate_constitutional_case_url 편의 메서드"""
        url = generator.generate_constitutional_case_url("2018헌바26")
        assert unquote(url) == "https://www.law.go.kr/헌재결정례/(2018헌바26)"

    def test_generate_interpretation_url(self, generator):
        """generate_interpretation_url 편의 메서드"""
        url = generator.generate_interpretation_url("법제처-2020-0001")
        assert unquote(url) == "https://www.law.go.kr/법령해석례/(법제처-2020-0001)"


class TestModuleLevelFunction:
    """모듈 레벨 함수 테스트"""

    def test_generate_law_url_function(self):
        """generate_law_url 편의 함수"""
        url = generate_law_url(category_code="STATUTE", title="민법")
        assert unquote(url) == "https://www.law.go.kr/법령/민법"


class TestUrlEncoding:
    """URL 인코딩 테스트"""

    def test_korean_encoding(self, generator):
        """한글 인코딩"""
        url = generator.generate_url(category_code="STATUTE", title="자동차관리법")
        # URL에 한글이 인코딩되어 있어야 함
        assert "자동차관리법" in unquote(url) or "%EC%9E%90%EB%8F%99%EC%B0%A8" in url

    def test_special_characters(self, generator):
        """특수문자 인코딩"""
        url = generator.generate_url(
            category_code="CASE_SUPREME",
            identifier="2013다214529"
        )
        # 괄호가 포함됨
        assert "(" in unquote(url) or "%28" in url

    def test_spaces_in_title(self, generator):
        """공백 포함 제목"""
        url = generator.generate_url(
            category_code="ADMIN_RULE",
            title="개인정보 보호지침"
        )
        # 공백이 인코딩되어야 함
        assert "개인정보 보호지침" in unquote(url) or "%20" in url


class TestErrorHandling:
    """에러 처리 테스트"""

    def test_invalid_category_code(self, generator):
        """잘못된 카테고리 코드"""
        with pytest.raises(ValueError, match="지원하지 않는 카테고리"):
            generator.generate_url(
                category_code="INVALID_CODE",
                title="테스트"
            )

    def test_committee_without_org_name(self, generator):
        """위원회 카테고리에서 org_name 누락"""
        with pytest.raises(ValueError, match="org_name"):
            generator.generate_url(
                category_code="COMMITTEE_TEST",
                title="테스트"
            )

    def test_system_map_without_subcategory(self, generator):
        """SYSTEM_MAP에서 subcategory 누락"""
        with pytest.raises(ValueError, match="subcategory"):
            generator.generate_url(
                category_code="SYSTEM_MAP",
                title="테스트"
            )


class TestBracketBuilding:
    """괄호 파라미터 빌드 테스트"""

    def test_empty_bracket(self, generator):
        """빈 괄호 파라미터"""
        bracket = generator._build_bracket()
        assert bracket == ""

    def test_single_value(self, generator):
        """단일 값"""
        bracket = generator._build_bracket("12345")
        assert "(12345)" in unquote(bracket)

    def test_multiple_values(self, generator):
        """복수 값"""
        bracket = generator._build_bracket("12345", "20210101")
        assert "(12345,20210101)" in unquote(bracket)

    def test_skip_none_values(self, generator):
        """None 값 스킵"""
        bracket = generator._build_bracket(None, "12345", None)
        assert "(12345)" in unquote(bracket)

    def test_skip_empty_values(self, generator):
        """빈 문자열 스킵"""
        bracket = generator._build_bracket("", "12345", "")
        assert "(12345)" in unquote(bracket)


class TestStaticMethods:
    """정적 메서드 테스트"""

    def test_url_segment_encoding(self):
        """URL segment 인코딩"""
        result = LawUrlGenerator._url_segment("민법")
        # 한글이 URL 인코딩됨
        assert "%" in result

    def test_url_segment_safe_chars(self):
        """안전 문자 처리"""
        result = LawUrlGenerator._url_segment("test123")
        # 영숫자는 그대로
        assert result == "test123"
