# Feature Specification: Paralegal Progress Dashboard

**Feature Branch**: `004-paralegal-progress`  
**Created**: 2025-02-21  
**Status**: Draft  
**Input**: User description: "Paralegal progress page and mid-demo feedback #92"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Monitor Case Throughput (Priority: P1)

As a paralegal, I want a single dashboard showing every case I own with its latest intake/AI/progress signals so that I know where to focus without opening five different tabs.

**Why this priority**: This replaces the manual spreadsheet noted in mid-demo feedback and enables daily operations for paralegals; without it, they cannot see stalled evidence or AI status.

**Independent Test**: Load `/staff/progress` with mock data and verify that each case card displays status, assignee, evidence counts, and AI analysis badge in <2 seconds with no API errors.

**Acceptance Scenarios**:

1. **Given** a paralegal has three active cases, **When** they open the dashboard, **Then** they see one card per case with status chips (e.g., "Evidence Uploading", "AI Draft Ready") plus evidence counts split by processing stage.
2. **Given** there are no assigned cases, **When** the page loads, **Then** an empty-state call-to-action ("No assigned cases yet") is displayed instead of a spinner.

---

### User Story 2 - Track Mid-Demo Feedback Tasks (Priority: P2)

As a paralegal, I need to review the 16 feedback action items (e.g., 판례 DB 연동, AI 역할 강화, evidence QA) for each case so that I can flag blockers and report back to lawyers.

**Why this priority**: The mid-demo review identified specific gaps; surfacing them per case ensures they get closed before final presentation.

**Independent Test**: Toggle mock checklist data for a case and verify that the dashboard highlights outstanding items, including counts and descriptions.

**Acceptance Scenarios**:

1. **Given** a case has 5 unresolved feedback items, **When** the paralegal expands the case detail, **Then** they see a checklist with 5 unchecked rows plus timestamps/owners.
2. **Given** a case completes all feedback, **When** the dashboard refreshes, **Then** the checklist collapses into a "Feedback complete" badge.

---

### User Story 3 - Surface Blocking Events (Priority: P3)

As a supervising lawyer, I want to filter progress by "blocked" status (missing evidence, AI error, client waiting) so I can reassign resources quickly.

**Why this priority**: Helps leadership manage throughput; while not required to render the page, it unlocks faster response to high-risk cases.

**Independent Test**: Apply the "Blocked" filter and confirm only cases with `is_blocked=true` from the API remain; API returns must support filter param.

**Acceptance Scenarios**:

1. **Given** two cases have failed AI ingestion, **When** the lawyer toggles "Show blocked only", **Then** only those cases are displayed with error context.
2. **Given** there are no blocked cases, **When** the filter is active, **Then** an informational empty-state is shown.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- What happens when the backend endpoint returns partial data (e.g., checklist missing)? → UI must fallback to "No feedback data yet" and log warning.
- How does system handle API failure/timeouts? → Display non-blocking toast immediately (0 retries, fail fast) + manual retry button; do not leave spinners forever.
- What if a paralegal has 50+ cases? → Pagination or lazy loading ensures performance (<500ms render per page).
- How to handle stale AI status? → Show last-updated timestamp and highlight if >24h old.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: Backend MUST expose `/staff/progress` (or equivalent) returning per-case status, evidence counts by stage, AI status, assigned paralegal, blocking flags.
- **FR-002**: Endpoint MUST accept optional filters (`?blocked=true`, `?assignee=...`) for lawyer oversight use cases.
- **FR-003**: Frontend MUST render a dashboard at `/staff/progress` restricted to paralegal/lawyer roles using existing auth context.
- **FR-004**: Each case card MUST show last updated timestamp, evidence totals, AI state (Pending, Processing, Draft Ready, Failed), and outstanding feedback count.
- **FR-005**: UI MUST provide a collapsible list of the 16 mid-demo feedback items per case, showing completion state and owner.
- **FR-006**: System MUST handle empty states gracefully (no cases, missing feedback data, API errors) with actionable messaging.
- **FR-007**: Page MUST refresh data on demand (manual refresh button) without full page reload.
- **FR-008**: Observability: log API latency + UI load duration to CloudWatch Logs (structured JSON format) for delay diagnosis.

### Key Entities

- **CaseProgressSummary**: Combines case metadata (`case_id`, `title`, `client_name`), assigned paralegal, `status`, evidence counts (`uploaded`, `in_processing`, `ai_ready`), AI draft status, `is_blocked`, `last_updated_at`.
- **FeedbackChecklistItem**: Represents one of the 16 feedback tasks with fields: `item_id`, `description`, `status` (pending/done), `updated_at`, `owner`, `notes`. Linked to `case_id`.
- **ProgressFilter**: Request payload representing filter/sort preferences (role-specific).

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Paralegal can identify their next blocked case within 30 seconds of opening `/staff/progress` (verified via manual QA checklist in T603).
- **SC-002**: API latency for `/staff/progress` stays under 400ms P95 for up to 200 cases.
- **SC-003**: 100% of the 16 mid-demo feedback tasks are surfaced with completion status per case.
- **SC-004**: After launch, at least 80% of weekly stand-up updates reference data pulled directly from this dashboard (self-reported survey).

---

## Clarifications

### Session 2025-12-08
- Q: Which logging sink should capture API latency and UI load metrics? → A: CloudWatch Logs (AWS native, structured JSON)
- Q: How should the 30-second usability metric (SC-001) be verified? → A: Manual QA checklist item in T603
- Q: How many automatic retry attempts for API failures before showing error toast? → A: 0 (fail fast, show error immediately with retry button)
