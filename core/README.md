# Core Shared Modules

이 디렉터리는 백엔드, AI 워커, 프론트엔드 간에 공유하는 파이썬/타입스크립트 모듈이 생겼을 때만 채웁니다. 공용 로직을 추가할 때는 다음 원칙을 지킵니다.

1. 재사용 빈도가 높은 도메인 모델, 상수, 커스텀 예외만 배치합니다.
2. Circular dependency 를 피하기 위해 계층 구조(contracts → clients → utils)로 정리합니다.
3. 각 모듈에는 README 또는 docstring 으로 사용 방법을 남깁니다.
