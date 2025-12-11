# MVP Readiness Checklist

**Feature**: 009-mvp-gap-closure (MVP 구현 갭 해소)
**Purpose**: Comprehensive requirements quality validation for production readiness
**Created**: 2025-12-09
**Updated**: 2025-12-11
**Depth**: Thorough (~87 items)
**Audience**: Author (self-validation)
**TDD Tests**: 75 tests (EvidenceReviewCard: 41, EvidenceMetadata: 34)

---

## Requirement Completeness

### US1 - AI Worker 실서비스 연동 (P1)

- [ ] CHK001 - Are S3 bucket naming conventions explicitly specified for dev/prod environments? [Completeness, Spec §FR-001]
- [ ] CHK002 - Are IAM permission requirements documented with specific actions (s3:GetObject, s3:PutObject)? [Completeness, Spec §FR-001]
- [ ] CHK003 - Is the S3 event trigger path pattern (`cases/{case_id}/raw/`) explicitly defined? [Completeness, Spec §FR-002]
- [ ] CHK004 - Are DynamoDB table naming and schema requirements documented? [Completeness, Spec §FR-003]
- [ ] CHK005 - Is the Qdrant collection naming pattern (`case_rag_{case_id}`) specified with isolation requirements? [Completeness, Spec §FR-004]
- [ ] CHK006 - Are Lambda timeout and memory requirements specified? [Gap]
- [ ] CHK007 - Are idempotency requirements for S3 event processing documented? [Completeness]

### US2 - Backend RAG/Draft (P1)

- [ ] CHK008 - Are RAG search API query parameters fully specified? [Completeness, Spec §FR-005]
- [ ] CHK009 - Is the Draft Preview response format with citation structure documented? [Completeness, Spec §FR-006]
- [ ] CHK010 - Are export format requirements (DOCX/PDF) specified with structure details? [Completeness, Spec §FR-007]
- [ ] CHK011 - Are search history storage requirements defined or explicitly deferred? [Gap, Plan §Backend RAG/Draft]

### US3 - Frontend 에러 처리 (P2)

- [ ] CHK012 - Are toast notification requirements specified for each error type? [Completeness, Spec §FR-008,009]
- [ ] CHK013 - Is the retry mechanism behavior (exponential backoff) quantified? [Gap]
- [ ] CHK014 - Are loading state naming conventions defined? [Gap, Plan §Frontend Error Handling]
- [ ] CHK015 - Are 401 redirect loop prevention requirements documented? [Completeness, Spec §FR-008]

### US4 - CI 테스트 커버리지 (P2)

- [ ] CHK016 - Is the target coverage threshold (65%→80%) specified with timeline? [Completeness, Spec §FR-011,012,013]
- [ ] CHK017 - Are integration test skip conditions explicitly defined? [Completeness, Spec §FR-011]
- [ ] CHK018 - Is the minimum test count (300) for AI Worker specified? [Completeness, Spec §FR-012]

### US5 - 권한 제어 (P2)

- [ ] CHK019 - Are all API endpoints requiring permission checks enumerated? [Completeness, Spec §FR-014]
- [ ] CHK020 - Is the audit log schema (user_id, action, timestamp, IP) fully specified? [Completeness, Spec §FR-016]
- [ ] CHK021 - Are case_member role permissions (OWNER/MEMBER/VIEWER) defined? [Completeness]

### US6 - 배포 파이프라인 (P3)

- [ ] CHK022 - Are staging/production deployment triggers explicitly defined? [Completeness, Spec §FR-017,018]
- [ ] CHK023 - Is the rollback procedure documented? [Gap, Spec §FR-019]
- [ ] CHK024 - Are deployment approval requirements (manual for prod) specified? [Completeness, Spec §FR-018]

### US7 - 법적 고지 및 약관 (P2) ✅ VERIFIED

- [x] CHK064 - Is copyright footer text explicitly specified? [Completeness, Spec §FR-020] ✅ T060 implemented in Footer.tsx
- [x] CHK065 - Are ToS and Privacy checkbox requirements distinct (separate checkboxes)? [Completeness, Spec §FR-021,022] ✅ T063 implemented in signup
- [x] CHK066 - Is Terms of Service content defined or referenced? [Gap, Spec §FR-023] ✅ T061,T068 - /terms page created
- [x] CHK067 - Is Privacy Policy PIPA compliance requirements listed? [Completeness, Spec §FR-024] ✅ T062,T069 - /privacy page created
- [ ] CHK068 - Is user_agreements schema specified (user_id, agreement_type, version, agreed_at)? [Completeness, Spec §FR-025] ⏳ Backend T064-T067 pending
- [ ] CHK069 - Are agreement re-consent requirements on policy version change defined? [Gap] ⏳ Deferred to post-MVP

### US8 - 정보 구조(IA) 개선 (P3) ✅ VERIFIED

- [x] CHK070 - Are specific features required in main navigation 1-depth? [Completeness, Spec §FR-026] ✅ T071 - LawyerNav updated
- [x] CHK071 - Is "1-click access" measurable (which elements, from which views)? [Clarity, Spec §FR-027] ✅ T072 - Case detail tabs implemented
- [x] CHK072 - Are back/home button behaviors defined for each page type? [Gap, Spec §FR-028] ✅ T073,T074 - IA guide created

### US9 - 회원가입 역할 선택 (P2) ✅ VERIFIED (Frontend)

- [x] CHK073 - Are available roles for self-signup explicitly enumerated? [Completeness, Spec §FR-029] ✅ T082 - lawyer/client/detective dropdown
- [x] CHK074 - Is role parameter format and validation specified? [Completeness, Spec §FR-030] ✅ T083 - API call with role param
- [x] CHK075 - Are role-to-dashboard path mappings documented? [Completeness, Spec §FR-031] ✅ T085 - Role redirect implemented
- [x] CHK076 - Is error message for missing role selection specified? [Completeness, Spec §FR-032] ✅ T086 - HTML5 required attribute

### US10 - 의뢰인(Client) 포털 (P2) ✅ TDD VERIFIED (41 tests)

- [ ] CHK077 - Is "assigned cases" definition clear (via case_members table)? [Clarity, Spec §FR-033] ⏳ Backend T088 pending
- [x] CHK078 - Is evidence review status enum defined (pending_review, approved, rejected)? [Completeness, Spec §FR-034,035] ✅ T092 - EvidenceReviewCard.test.tsx (41 tests)
- [x] CHK079 - Are review workflow permissions specified (who can approve/reject)? [Completeness] ✅ T092 - Lawyer-only approve/reject buttons
- [ ] CHK080 - Is client-to-lawyer messaging scope defined (1:1 per case)? [Gap, Spec §FR-036] ⏳ Messaging already implemented
- [ ] CHK081 - Are 403 scenarios for unauthorized case access documented? [Completeness] ⏳ Backend T095 pending

### US11 - 탐정(Detective) 포털 (P2) ✅ TDD VERIFIED (34 tests)

- [ ] CHK082 - Is detective case assignment mechanism defined? [Gap, Spec §FR-037] ⏳ Via case_members table
- [x] CHK083 - Are supported EXIF fields listed (GPS, datetime, etc.)? [Completeness, Spec §FR-038] ✅ T103 - EvidenceMetadata.test.tsx (34 tests): GPS, altitude, accuracy, datetime, camera, software, resolution, ISO, shutter, aperture, focal length, flash
- [x] CHK084 - Is EXIF extraction failure handling specified? [Gap] ✅ T103 - Empty state "메타데이터를 찾을 수 없습니다" message
- [x] CHK085 - Are earnings data fields defined (amount, status, dates)? [Completeness, Spec §FR-039] ✅ T102 - Earnings page connected
- [ ] CHK086 - Is detective_earnings table schema specified? [Completeness, Spec §FR-040] ⏳ Backend T097-T100 pending
- [ ] CHK087 - Are earnings status transitions defined (pending → paid)? [Completeness] ⏳ Backend implementation pending

---

## Requirement Clarity

- [ ] CHK025 - Is "5분 내 분석 완료" quantified with specific conditions (file size, type)? [Clarity, Spec §SC-001]
- [ ] CHK026 - Is "2초 이내 RAG 검색" measured under what load conditions? [Clarity, Spec §SC-002]
- [ ] CHK027 - Is "30초 내 Draft 생성" measured for what document size? [Clarity, Spec §SC-003]
- [ ] CHK028 - Is "사용자 친화적 메시지" defined with specific examples? [Ambiguity, Spec §SC-008]
- [ ] CHK029 - Is "권한 없는 접근 시 100% 403" testable with defined test cases? [Clarity, Spec §SC-006]
- [ ] CHK030 - Are "분석된 증거" criteria for Draft generation clearly defined? [Clarity, Spec §US2]

---

## Requirement Consistency

- [ ] CHK031 - Do coverage thresholds align between pytest.ini (65%) and CLAUDE.md target (80%)? [Conflict, Plan §CI Tests]
- [ ] CHK032 - Are error handling patterns consistent between frontend error boundaries and API client? [Consistency]
- [ ] CHK033 - Is permission check behavior (403 vs 404) consistent across all case-related APIs? [Consistency, Plan §Permissions]
- [ ] CHK034 - Are S3 bucket names consistent across AI Worker, Backend, and CI configurations? [Consistency]
- [ ] CHK035 - Is audit log format consistent between AuditLog model and audit_service.py? [Consistency]

---

## Acceptance Criteria Quality

- [ ] CHK036 - Are US1 acceptance scenarios testable without manual AWS console access? [Measurability, Spec §US1]
- [ ] CHK037 - Can "관련도 순으로 증거 목록 반환" be objectively verified? [Measurability, Spec §US2]
- [ ] CHK038 - Is "사용자 친화적 메시지 표시율 100%" measurable? [Measurability, Spec §SC-008]
- [ ] CHK039 - Can "10분 내 배포 완료" be automated and measured? [Measurability, Spec §SC-007]

---

## Scenario Coverage

### Primary Flows

- [ ] CHK040 - Is the happy path for evidence upload → AI analysis → draft generation fully specified? [Coverage]

### Alternate Flows

- [ ] CHK041 - Are requirements defined for partial AI analysis failure (some parsers fail)? [Coverage, Gap]
- [ ] CHK042 - Are requirements specified for draft generation with incomplete evidence? [Coverage, Gap]

### Exception/Error Flows

- [ ] CHK043 - Is Lambda timeout handling (15min) specified with user notification? [Coverage, Spec §Edge Cases]
- [ ] CHK044 - Is Qdrant connection failure behavior defined (graceful degradation)? [Coverage, Spec §Edge Cases]
- [ ] CHK045 - Are DynamoDB throttling scenarios addressed? [Gap]

### Recovery Flows

- [ ] CHK046 - Is the retry queue behavior for failed vector storage defined? [Coverage, Spec §Edge Cases]
- [ ] CHK047 - Are rollback requirements specified for failed deployments? [Gap, Spec §FR-019]
- [ ] CHK048 - Is session recovery behavior after 401 redirect defined? [Gap]

---

## Non-Functional Requirements

### Performance

- [ ] CHK049 - Are cold start requirements for Lambda defined? [Gap]
- [ ] CHK050 - Are concurrent user load requirements specified? [Gap]

### Security

- [ ] CHK051 - Are JWT token expiry and refresh requirements documented? [Completeness]
- [ ] CHK052 - Is the audit log retention policy specified? [Gap]
- [ ] CHK053 - Are S3 presigned URL expiry requirements (5min) documented? [Completeness]

### Accessibility

- [ ] CHK054 - Are accessibility requirements defined for error toast notifications? [Gap]

---

## Dependencies & Assumptions

- [ ] CHK055 - Is the Qdrant Cloud instance assumption validated? [Assumption, Spec §Assumptions]
- [ ] CHK056 - Is OpenAI API key environment variable assumption documented? [Assumption, Spec §Assumptions]
- [ ] CHK057 - Are GitHub Secrets for AWS credentials documented? [Dependency, Research §Unresolved]
- [ ] CHK058 - Is the existing test code validity assumption verified? [Assumption, Spec §Assumptions]

---

## Constitution Compliance

- [ ] CHK059 - Is Evidence Integrity (SHA-256 hash, audit trail) enforced in all evidence flows? [Constitution §I]
- [ ] CHK060 - Is Case Isolation (`case_rag_{case_id}`) enforced with no cross-case queries? [Constitution §II]
- [ ] CHK061 - Is No Auto-Submit principle maintained (Draft as "Preview Only")? [Constitution §III]
- [ ] CHK062 - Is AWS-Only Data Storage requirement satisfied (no external storage)? [Constitution §IV]
- [x] CHK063 - Is TDD Cycle compliance documented for new test additions? [Constitution §VII] ✅ 75 TDD tests (US10: 41, US11: 34)

---

## Summary

| Category | Items | Verified | Coverage |
|----------|-------|----------|----------|
| Requirement Completeness | 48 | 17 | US1-US11 |
| Requirement Clarity | 6 | 0 | Performance metrics, UX terms |
| Requirement Consistency | 5 | 0 | Cross-module alignment |
| Acceptance Criteria Quality | 4 | 0 | Measurability |
| Scenario Coverage | 9 | 0 | Primary/Alternate/Exception/Recovery |
| Non-Functional Requirements | 6 | 0 | Performance, Security, A11y |
| Dependencies & Assumptions | 4 | 0 | External dependencies |
| Constitution Compliance | 5 | 1 | NON-NEGOTIABLE principles |
| **Total** | **87** | **18** | **21% verified** |

### Verification Status by User Story

| User Story | Status | Frontend | Backend | Notes |
|------------|--------|----------|---------|-------|
| US7 (Legal/Terms) | ✅ 4/6 | Complete | Pending | T064-T067 backend needed |
| US8 (IA) | ✅ 3/3 | Complete | N/A | All tasks done |
| US9 (Role Signup) | ✅ 4/4 | Complete | Pending | T084 backend verification |
| US10 (Client Portal) | ✅ 2/5 | Complete | Pending | 41 TDD tests, backend T088-T095 |
| US11 (Detective Portal) | ✅ 3/6 | Complete | Pending | 34 TDD tests, backend T096-T105 |

---

## Usage

1. Review each item before implementation
2. Mark items as checked `[x]` when requirements are confirmed clear/complete
3. Add `[CLARIFIED]` marker with explanation for items requiring spec updates
4. Escalate `[BLOCKED]` items that cannot be resolved without stakeholder input

---

## Next Actions (Priority Order)

1. **Backend T064-T067**: user_agreements table + signup API integration (US7)
2. **Backend T084**: Verify role parameter acceptance in signup API (US9)
3. **Backend T088-T095**: Client portal API verification (US10)
4. **Backend T096-T105**: Detective portal API + EXIF service (US11)
5. **Phase 2-4**: AWS infrastructure + AI Worker + RAG/Draft verification (US1, US2)
