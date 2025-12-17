"""에러 메시지 상수 정의

이 파일은 API 응답에 사용되는 에러 메시지를 중앙 관리합니다.
하드코딩된 문자열 대신 이 상수를 사용하세요.
"""


class ErrorMessages:
    """HTTP 에러 응답에 사용되는 메시지 상수"""

    # 권한 관련 (403 Forbidden)
    PERMISSION_DENIED = "접근 권한이 없습니다"
    CASE_PERMISSION_DENIED = "이 케이스에 접근 권한이 없습니다."

    # Not Found (404)
    CASE_NOT_FOUND = "사건을 찾을 수 없습니다"
    CASE_NOT_FOUND_OR_NO_ACCESS = "케이스를 찾을 수 없거나 접근 권한이 없습니다."
    EVIDENCE_NOT_FOUND = "증거를 찾을 수 없습니다"
    CLIENT_NOT_FOUND = "의뢰인을 찾을 수 없습니다"
    DETECTIVE_NOT_FOUND = "탐정 연락처를 찾을 수 없습니다"
    CLIENT_DASHBOARD_NOT_FOUND = "의뢰인 대시보드를 찾을 수 없습니다"
    DETECTIVE_DASHBOARD_NOT_FOUND = "탐정 대시보드를 찾을 수 없습니다"
