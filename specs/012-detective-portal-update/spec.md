# Feature Specification: Detective Portal Update

**Feature ID:** 012-detective-portal-update
**Status:** Draft
**Created:** 2025-12-12
**Owner:** P (Frontend)

---

## Overview

Detective 포털 기능 업데이트 - 불필요한 기능 제거 및 의뢰 관리 기능 개선

## User Stories

### US1: 현장기록 기능 제거
**As a** Detective 사용자
**I want** 사용하지 않는 현장기록 기능이 제거되기를
**So that** UI가 간결하고 필요한 기능에 집중할 수 있다

**Acceptance Criteria:**
- AC-001: 현장기록 페이지 (`/detective/field`) 제거
- AC-002: 네비게이션에서 현장기록 메뉴/버튼 제거
- AC-003: FieldRecorder, GPSTracker 등 관련 컴포넌트 제거

### US2: 의뢰관리 CRUD
**As a** Detective 사용자
**I want** 의뢰를 조회/생성/수정/삭제할 수 있기를
**So that** 할당된 조사 의뢰를 효율적으로 관리할 수 있다

**Acceptance Criteria:**
- AC-004: 의뢰 목록 조회 (pagination)
- AC-005: 의뢰 상세 조회
- AC-006: 의뢰 상태 업데이트
- AC-007: 의뢰 메모/노트 추가

### US3: CaseStatus Enum 버그 수정
**As a** Detective 사용자
**I want** 의뢰 목록이 정상 로드되기를
**So that** 500 에러 없이 의뢰를 확인할 수 있다

**Acceptance Criteria:**
- AC-008: `pending` status 쿼리 시 오류 없음
- AC-009: 모든 유효한 case status로 필터링 가능

---

## Functional Requirements

### FR-001: 현장기록 기능 삭제
- 삭제 대상 페이지: `/detective/field`
- 삭제 대상 컴포넌트: `FieldRecorder`, `GPSTracker`, 관련 UI
- 네비게이션 메뉴에서 제거

### FR-002: 의뢰 목록 API
- Endpoint: `GET /detective/cases`
- 필터: status, date range
- Pagination 지원

### FR-003: 의뢰 상세 API
- Endpoint: `GET /detective/cases/{id}`
- 반환: case 정보, 증거 목록, 메모

### FR-004: CaseStatus Enum 정합성
- DB enum에 `pending`, `completed` 추가 (또는 매핑)
- Python schema와 DB enum 일치

---

## Out of Scope

- 새로운 기능 추가 (기존 기능 정리 및 버그 수정만)
- Lawyer/Client 포털 변경
- AI Worker 연동

---

## Dependencies

- **Issue #293**: CaseStatus enum 불일치 버그 (H 담당)
- **Backend API**: Detective portal endpoints

---

## Success Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| SC-001 | 현장기록 페이지/버튼 완전 제거 | Manual inspection |
| SC-002 | 의뢰 목록 정상 로드 (500 에러 없음) | E2E test |
| SC-003 | 의뢰 상태 필터링 동작 | Unit test |
| SC-004 | Detective 대시보드 정상 동작 | Manual test |

---

## Technical Notes

### CaseStatus Enum Issue
```
DB enum (models.py):     active, open, in_progress, closed
Schema enum:             active, pending, completed, closed
```
`pending`/`completed` 불일치로 인한 PostgreSQL 쿼리 에러.

### Files to Remove (US1)
- `frontend/src/app/detective/field/page.tsx`
- `frontend/src/components/detective/FieldRecorder.tsx`
- `frontend/src/components/detective/GPSTracker.tsx`
- Related tests and imports
