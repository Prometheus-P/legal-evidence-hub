<!--
SYNC IMPACT REPORT
==================
Version change: 1.2.0 → 1.3.0

Modified principles: None

Added sections:
- Team Responsibilities: GitHub account mappings added
- Collaboration: GitHub Issue Assignment Policy (role-based)

Removed sections: None

Templates validated:
- .specify/templates/plan-template.md ✅ (No updates needed)
- .specify/templates/spec-template.md ✅ (No updates needed)
- .specify/templates/tasks-template.md ✅ (No updates needed)

Follow-up TODOs: None
-->

# Legal Evidence Hub (LEH) Constitution

## Core Principles

### I. Evidence Integrity (NON-NEGOTIABLE)

All evidence uploads MUST generate SHA-256 hash stored in audit logs. Chain of Custody MUST be maintained for all evidence files. All CRUD operations MUST be logged in the immutable `audit_logs` table.

**Rationale**: Legal evidence requires cryptographic verification and complete audit trail for court admissibility. Any compromise of evidence integrity invalidates the platform's core value proposition.

### II. Case Isolation (NON-NEGOTIABLE)

Each case MUST have an isolated RAG index using the pattern `case_rag_{case_id}` in Qdrant. Cross-case data queries are FORBIDDEN. On case closure, the Qdrant collection MUST be deleted and DynamoDB records MUST be soft-deleted.

**Rationale**: Divorce cases contain sensitive personal information. Accidental cross-case data leakage could violate attorney-client privilege and privacy regulations (PIPA).

### III. No Auto-Submit (NON-NEGOTIABLE)

AI-generated outputs (drafts, summaries, labels) MUST be presented as "Preview Only". The system MUST NOT auto-submit any AI output to external systems. Lawyers MUST manually review and approve all generated content before any external use.

**Rationale**: Legal liability requires human attorney oversight. AI assistance is advisory only; final document decisions are the attorney's sole responsibility.

### IV. AWS-Only Data Storage

All evidence data MUST remain within AWS infrastructure (S3, DynamoDB, Qdrant on EC2). External storage services (Google Drive, Dropbox, etc.) are FORBIDDEN. All data MUST stay within a single AWS account.

**Rationale**: Centralized AWS storage ensures consistent security controls, audit capabilities, and compliance with data sovereignty requirements.

### V. Clean Architecture with Repository Pattern

Backend code MUST follow the layered pattern: **Routers → Services → Repositories → DB/External Services**.

**Layer Responsibilities**:
- **Routers (API)**: Handle HTTP concerns only (request parsing, response formatting, status codes). MUST NOT contain business logic.
- **Services**: Contain business logic, orchestrate repositories, enforce business rules. MUST NOT directly access database or external APIs.
- **Repositories**: Handle data persistence with single-entity focus. Each repository MUST manage ONE entity type. MUST NOT contain business logic or call other repositories directly.
- **Utils**: Stateless helpers for cross-cutting concerns (S3, OpenAI clients). MUST NOT maintain state.

**Repository Pattern Requirements**:
- Each domain entity MUST have a dedicated repository (e.g., `CaseRepository`, `EvidenceRepository`, `PartyRepository`)
- Repositories MUST expose CRUD methods: `create()`, `get_by_id()`, `get_all()`, `update()`, `delete()`
- Complex queries spanning multiple entities MUST be orchestrated in the Service layer, not repositories
- Repository methods MUST NOT call Service methods (no circular dependencies)

**Rationale**: The repository pattern provides a clean abstraction over data access, enabling independent unit testing with mocked repositories, database technology flexibility, and maintainable codebase as the platform grows.

### VI. Branch Protection

Direct pushes to `main` and `dev` branches are FORBIDDEN. All code changes to protected branches MUST go through Pull Requests. Documentation-only changes (*.md files) MAY be pushed directly to main.

**Rationale**: PR-based workflow ensures code review, prevents accidental production deployments, and maintains clear audit trail of changes.

### VII. TDD Cycle

When tests are requested or specified in a feature, tests MUST be written FIRST and MUST FAIL before implementation begins. The Red-Green-Refactor cycle MUST be followed:
1. **Red**: Write a failing test that defines expected behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code quality while keeping tests green

Test files MUST be committed separately or alongside implementation with clear commit messages indicating TDD phase.

**Rationale**: Test-Driven Development ensures code correctness from inception, prevents regression, documents expected behavior, and produces inherently testable designs. Writing tests first forces developers to think about API contracts and edge cases before implementation.

### VIII. Semantic Versioning

All application releases MUST follow Semantic Versioning (SemVer) with the format `MAJOR.MINOR.PATCH`:
- **MAJOR**: Incremented for backward-incompatible API changes or breaking changes
- **MINOR**: Incremented for new features that are backward-compatible
- **PATCH**: Incremented for backward-compatible bug fixes

Version tags MUST be created for all releases using the format `vX.Y.Z` (e.g., `v1.2.0`). Each version tag MUST include a changelog entry describing changes. Pre-release versions SHOULD use suffixes like `-alpha`, `-beta`, `-rc.1`.

**Rationale**: Semantic versioning enables clear communication of change impact to users and integrators. Consistent versioning supports automated dependency management, rollback procedures, and release documentation.

## Development Constraints

### Technology Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+
- **Storage**: PostgreSQL (RDS), AWS S3, DynamoDB, Qdrant
- **AI**: OpenAI (GPT-4o, Whisper, Vision)
- **CDN**: AWS CloudFront

### Security Requirements

- JWT-based authentication with HTTP-only cookies
- Role-based access control (RBAC) at case level
- S3 presigned URLs for evidence uploads (5-minute expiry)
- Security headers via middleware
- No sensitive data in logs

### Testing Requirements

- Backend: pytest with 80% coverage target for AI Worker
- Frontend: Jest + React Testing Library
- Unit tests for services/repositories with mocked dependencies
- Integration tests for full API endpoints
- E2E tests with Playwright for critical user flows
- TDD cycle MUST be followed when tests are specified in feature requirements

## Collaboration & Branch Strategy

### Branch Hierarchy

```
main ← dev ← feat/*
```

- **main**: Production-ready code, deployed to CloudFront production
- **dev**: Staging integration, deployed to CloudFront staging
- **feat/***: Feature branches for active development

### PR Rules

- Direction: Always `feat/* → dev → main`
- Minimum 1 reviewer required
- Tests MUST pass before merge
- Use PR template from `.github/PULL_REQUEST_TEMPLATE.md`

### Team Responsibilities

| Role | GitHub | Responsibility |
|:-----|:-------|:---------------|
| H (Backend/Infra) | `leaf446` | FastAPI, RDS, S3, authentication, deployment |
| L (AI/Data) | `vsun410` | AI Worker, STT/OCR, parsers, embeddings, RAG |
| P (Frontend/PM) | `Prometheus-P` | Next.js, UX, GitHub operations, PR approval |

### GitHub Issue Assignment Policy

All GitHub issues MUST be assigned based on the responsible domain area:

| Domain | Assignee | Scope |
|:-------|:---------|:------|
| **AI Worker** | `vsun410` | `ai_worker/`, AWS Lambda, S3 events, DynamoDB, Qdrant storage |
| **Backend** | `leaf446` | `backend/`, FastAPI, API endpoints, Services, Repositories |
| **Frontend** | `Prometheus-P` | `frontend/`, Next.js, React components, UI/UX |

**Assignment Rules**:
- Issues spanning multiple domains MUST assign all relevant owners
- Setup/documentation issues MAY assign all team members
- gh CLI format: `--assignee <username>` (e.g., `--assignee vsun410`)

**Rationale**: Clear ownership ensures accountability, reduces confusion, and enables parallel work streams without conflicts.

## Governance

### Amendment Process

1. Proposed changes MUST be documented with rationale
2. Changes affecting NON-NEGOTIABLE principles require team consensus
3. All amendments MUST update the version and Last Amended date
4. Dependent templates MUST be reviewed for consistency after amendments

### Versioning Policy

- **MAJOR**: Backward incompatible changes to NON-NEGOTIABLE principles
- **MINOR**: New principle or section added, material guidance expansion
- **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Review

- All PRs MUST verify compliance with Constitution principles
- Code reviews SHOULD reference relevant principles when requesting changes
- Complexity additions MUST be justified against Clean Architecture principle
- Test-related PRs MUST demonstrate TDD cycle compliance when applicable
- New backend features MUST follow Repository Pattern per Principle V
- Release PRs MUST include version bump following Semantic Versioning principle
- GitHub issues MUST be assigned per the Issue Assignment Policy

**Version**: 1.3.0 | **Ratified**: 2025-12-03 | **Last Amended**: 2025-12-09
