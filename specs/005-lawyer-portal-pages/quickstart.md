# Quickstart: 005-lawyer-portal-pages

**Purpose**: Rapid onboarding for implementing lawyer portal pages feature.

---

## Feature Overview

Fix 404 errors on existing lawyer portal pages and implement missing pages:
- `/lawyer/clients` - Client management (NEW)
- `/lawyer/investigators` - Investigator management (NEW)
- `/settings` - User settings hub (NEW)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
├─────────────────────────────────────────────────────────────┤
│  /lawyer/clients       → useClients() → GET /lawyer/clients │
│  /lawyer/investigators → useInvestigators() → GET /lawyer/investigators │
│  /settings            → useSettings() → GET /settings/*     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
├─────────────────────────────────────────────────────────────┤
│  lawyer_clients.py     → ClientService → CaseRepository     │
│  lawyer_investigators.py → InvestigatorService → CaseRepo   │
│  settings.py           → SettingsService → UserRepository   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database (PostgreSQL)                      │
├─────────────────────────────────────────────────────────────┤
│  users (role='client') ←──┐                                  │
│  users (role='detective') ←──┼── case_members ←── cases      │
│  user_settings (optional)    │                               │
└─────────────────────────────────────────────────────────────┘
```

## Key Files to Modify/Create

### Backend (Priority Order)

1. **Fix merge conflict** (BLOCKING):
   ```
   backend/app/api/lawyer_portal.py  # Lines 209-211 have conflict markers
   ```

2. **New API routers**:
   ```
   backend/app/api/lawyer_clients.py      # GET /lawyer/clients, /lawyer/clients/{id}
   backend/app/api/lawyer_investigators.py # GET /lawyer/investigators, /lawyer/investigators/{id}
   backend/app/api/settings.py            # GET/PUT /settings/*
   ```

3. **New services**:
   ```
   backend/app/services/client_list_service.py
   backend/app/services/investigator_list_service.py
   backend/app/services/settings_service.py
   ```

4. **New schemas**:
   ```
   backend/app/schemas/client_list.py
   backend/app/schemas/investigator_list.py
   backend/app/schemas/settings.py
   ```

### Frontend (Priority Order)

1. **Missing pages** (cause of 404):
   ```
   frontend/src/app/lawyer/clients/page.tsx          # NEW
   frontend/src/app/lawyer/investigators/page.tsx    # NEW
   frontend/src/app/settings/page.tsx                # NEW
   frontend/src/app/settings/profile/page.tsx        # NEW
   frontend/src/app/settings/notifications/page.tsx  # NEW
   ```

2. **Hooks**:
   ```
   frontend/src/hooks/useClients.ts
   frontend/src/hooks/useInvestigators.ts
   frontend/src/hooks/useSettings.ts
   ```

3. **API clients**:
   ```
   frontend/src/lib/api/clients.ts
   frontend/src/lib/api/investigators.ts
   frontend/src/lib/api/settings.ts
   ```

4. **Components**:
   ```
   frontend/src/components/lawyer/ClientCard.tsx
   frontend/src/components/lawyer/ClientTable.tsx
   frontend/src/components/lawyer/InvestigatorCard.tsx
   frontend/src/components/settings/ProfileForm.tsx
   frontend/src/components/settings/NotificationSettings.tsx
   ```

## Quick Commands

```bash
# Backend development
cd backend
uvicorn app.main:app --reload

# Run backend tests
pytest tests/test_api/test_lawyer_clients.py -v
pytest tests/test_api/test_lawyer_investigators.py -v
pytest tests/test_api/test_settings.py -v

# Frontend development
cd frontend
npm run dev

# Run frontend tests
npm test src/app/lawyer/clients/
npm test src/app/lawyer/investigators/
npm test src/app/settings/

# Type check
npx tsc --noEmit
```

## Existing Patterns to Follow

### Backend Service Pattern
```python
# From backend/app/services/case_list_service.py
class ClientListService:
    def __init__(self, db: Session):
        self.db = db

    def get_clients(self, user_id: str, filters: ClientFilter, ...) -> ClientListResponse:
        # Query case_members + users where role='client'
        # Apply filters, pagination
        # Return ClientListResponse
```

### Frontend Hook Pattern
```typescript
// From frontend/src/hooks/useCaseList.ts
export function useClients() {
  const [clients, setClients] = useState<ClientItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<ClientFilter>({});

  useEffect(() => {
    fetchClients();
  }, [filters]);

  return { clients, isLoading, error, filters, setFilters };
}
```

### Page Component Pattern
```typescript
// Standard 'use client' page with hook
'use client';

import { useClients } from '@/hooks/useClients';

export default function LawyerClientsPage() {
  const { clients, isLoading, error } = useClients();

  if (isLoading) return <LoadingSkeleton />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6">
      <h1>의뢰인 관리</h1>
      <ClientTable clients={clients} />
    </div>
  );
}
```

## Test Data

For development, use mock data fallback in hooks:

```typescript
const MOCK_CLIENTS: ClientItem[] = [
  {
    id: 'mock-client-1',
    name: '김민수',
    email: 'client1@example.com',
    phone: '010-1234-5678',
    case_count: 2,
    status: 'active',
  },
  // ...
];
```

## Deployment Notes

- All pages use App Router (Next.js 14)
- Trailing slash enabled in `next.config.js`
- Static export commented out (server-side rendering)
- CloudFront deployment via S3

## Related Specs

- [spec.md](./spec.md) - Feature requirements
- [research.md](./research.md) - Technical research findings
- [data-model.md](./data-model.md) - Data entities
- [contracts/](./contracts/) - API contracts
