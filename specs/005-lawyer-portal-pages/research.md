# Research: Lawyer Portal Pages

**Created**: 2025-12-08
**Status**: Complete

## 1. Root Cause Analysis: 404 Errors

### Findings

**The 404 errors are NOT caused by:**
- Static export configuration (Next.js `output: 'export'` is commented out in `next.config.js`)
- Middleware routing issues (middleware correctly handles `/cases` redirect by role)
- Missing layouts (lawyer layout exists with all nav items configured)

**The 404 errors ARE caused by:**
- Empty directories exist for routes but have no `page.tsx` files:
  - `/lawyer/clients/` - directory exists, empty
  - `/lawyer/investigators/` - directory exists, empty
  - `/settings/` - only has `/settings/billing/page.tsx`, no main `/settings/page.tsx`

### Page Status Inventory

| Route | Directory | page.tsx | Status |
|-------|-----------|----------|--------|
| `/lawyer/dashboard` | exists | exists | ✅ Working |
| `/lawyer/cases` | exists | exists | ✅ Code complete |
| `/lawyer/cases/[id]` | exists | exists | ✅ Code complete |
| `/lawyer/calendar` | exists | exists | ✅ Code complete |
| `/lawyer/messages` | exists | exists | ✅ Code complete |
| `/lawyer/billing` | exists | exists | ✅ Code complete |
| `/lawyer/clients` | exists | **MISSING** | ❌ 404 |
| `/lawyer/investigators` | exists | **MISSING** | ❌ 404 |
| `/settings` | exists | **MISSING** | ❌ 404 |
| `/settings/billing` | exists | exists | ✅ Code exists |
| `/cases` | exists | exists | ✅ Middleware redirects |

### Known Issue
- `backend/app/api/lawyer_portal.py` has merge conflict markers (lines 209-211) that need resolution

---

## 2. Backend API Availability

### Existing Endpoints (can be reused)

| Endpoint | Purpose | File |
|----------|---------|------|
| `GET /lawyer/dashboard` | Dashboard stats | `lawyer_portal.py` |
| `GET /lawyer/cases` | Case list with filters | `lawyer_portal.py` |
| `GET /lawyer/cases/{case_id}` | Case detail | `lawyer_portal.py` |
| `POST /lawyer/cases/bulk-action` | Bulk operations | `lawyer_portal.py` |
| `GET /lawyer/analytics` | Charts data | `lawyer_portal.py` |
| `GET /billing/*` | Billing endpoints | `billing.py` |
| `GET /calendar/*` | Calendar events | `calendar.py` |
| `GET /messages/*` | Messaging | `messages.py` |

### Missing Endpoints (need implementation)

| Endpoint | Purpose | Notes |
|----------|---------|-------|
| `GET /lawyer/clients` | List clients for lawyer | Can derive from cases - clients are linked via `case_members` |
| `GET /lawyer/clients/{client_id}` | Client details | User profile + linked cases |
| `GET /lawyer/investigators` | List investigators | Users with `detective` role assigned to lawyer's cases |
| `GET /lawyer/investigators/{id}` | Investigator details | User profile + case assignments |
| `GET /settings/profile` | User profile settings | May already exist in auth |
| `PUT /settings/profile` | Update profile | |
| `GET /settings/notifications` | Notification prefs | |
| `PUT /settings/notifications` | Update notifications | |

---

## 3. Data Model Analysis

### Client Entity (derived from existing models)
Clients are users with `role='client'` linked to cases via `case_members` table.

```python
# Existing in app/db/models.py
class User:
    id, email, name, role  # role can be 'client'

class CaseMember:
    case_id, user_id, role  # role can be 'CLIENT'
```

**To get lawyer's clients:**
```sql
SELECT DISTINCT u.* FROM users u
JOIN case_members cm ON u.id = cm.user_id
JOIN cases c ON cm.case_id = c.id
WHERE c.owner_id = :lawyer_id AND u.role = 'client'
```

### Investigator Entity (derived from existing models)
Investigators are users with `role='detective'` linked to cases.

**To get lawyer's investigators:**
```sql
SELECT DISTINCT u.* FROM users u
JOIN case_members cm ON u.id = cm.user_id
JOIN cases c ON cm.case_id = c.id
WHERE c.owner_id = :lawyer_id AND u.role = 'detective'
```

---

## 4. Frontend Patterns to Follow

### Component Structure (from existing pages)
```
frontend/src/
├── app/lawyer/{page}/
│   └── page.tsx           # 'use client' page component
├── components/lawyer/
│   └── {Component}.tsx    # Feature-specific components
├── hooks/
│   └── use{Feature}.ts    # Data fetching hooks (SWR pattern)
├── lib/api/
│   └── {feature}.ts       # API client functions
└── types/
    └── {feature}.ts       # TypeScript interfaces
```

### Existing Hooks Pattern
From `useCaseList.ts`:
- Uses `useState` for local state (filters, pagination)
- Returns loading, error, data states
- Provides setters for filters, pagination
- Uses mock data fallback for development

### Layout Integration
Sidebar navigation is already configured in `lawyer/layout.tsx`:
```typescript
const lawyerNavItems: NavItem[] = [
  { id: 'clients', label: '의뢰인 관리', href: '/lawyer/clients', ... },
  { id: 'investigators', label: '탐정/조사원', href: '/lawyer/investigators', ... },
];
```

---

## 5. Settings Page Analysis

### Current State
- `/settings/billing/page.tsx` exists
- No main `/settings/page.tsx` for navigation
- No profile or notification settings pages

### Proposed Structure
```
frontend/src/app/settings/
├── page.tsx              # Settings index (redirects or shows menu)
├── profile/
│   └── page.tsx          # Profile management
├── notifications/
│   └── page.tsx          # Notification preferences
├── security/
│   └── page.tsx          # Password, 2FA
└── billing/
    └── page.tsx          # Existing
```

---

## 6. Implementation Priority

Based on spec priorities and dependencies:

### Phase 1: Fix Routing/404 (P1)
- Pages with existing code should work
- Verify deployment builds correctly
- Check for any build-time errors

### Phase 2: Client Management (P2)
- Backend: Add `/lawyer/clients` endpoint
- Frontend: Create page + components
- Lower complexity (data exists, just need UI)

### Phase 3: Investigator Management (P2)
- Backend: Add `/lawyer/investigators` endpoint
- Frontend: Create page + components
- Similar pattern to clients

### Phase 4: Settings & Cases Redirect (P3)
- Settings: Create hub page + profile section
- `/cases` redirect: Already handled by middleware ✅

---

## 7. Open Questions (Resolved)

1. **Q: Why do pages with code show 404?**
   - A: Need to verify build/deployment process. Pages exist in source.

2. **Q: Are backend APIs needed for clients/investigators?**
   - A: Yes, need new endpoints. Data can be derived from existing models.

3. **Q: Should `/settings` be role-specific?**
   - A: No, settings should be universal (all roles). Use common layout.
