---
name: "🐞 Bug Report"
about: "동작 오류 · 예외 상황 신고"
title: "[Bug] "
labels: ["bug"]
assignees: []
---

## 🐞 버그 요약 (Summary)

- 한 줄 설명:
- 발생 위치(페이지/엔드포인트):
- 심각도(Impact): [ ] Blocker [ ] Major [ ] Minor

## ⚙️ 실행 환경

- 날짜/시간 (KST):
- OS / 브라우저 or 클라이언트 버전:
- 브랜치 / 커밋:
- Backend URL:
- Frontend URL:

## 🔁 재현 절차 (Reproduction Steps)
>
> 예시는 지우고 실제 수행한 명령과 UI 단계를 순서대로 작성하세요.

1. `uvicorn backend.main:app --reload`
2. `cd frontend && npm run dev`
3. 브라우저에서 <http://localhost:5173> 접속
4. 사건 상세 → "증거 타임라인" 클릭 → 오류 발생

## ✅ 기대한 동작 (Expected Behavior)

-

## 🚨 실제 동작 / 로그 (Actual Behavior / Logs)

- 실제 증상:
- 서버/브라우저 로그 링크 또는 첨부:

## 📎 관련 항목

- 관련 기능/페이지:
- 참고 Issue/PR:

## 🧩 추가 메모 (선택)

- 임시 우회 방법, 의심 원인 등 자유롭게 작성합니다.

## ✔️ 제출 체크리스트

- [ ] 최신 `develop` 기반에서 재현했습니다.
- [ ] 재현 절차를 단계별로 작성했습니다.
- [ ] 관련 로그/스크린샷을 첨부했습니다.
