# Data Model: Lawyer Portal Pages

**Created**: 2025-12-08
**Source**: spec.md analysis + existing models research

---

## Existing Models (Reused)

### User Model
```
User {
  id: string (UUID)
  email: string
  name: string
  role: enum ['admin', 'lawyer', 'staff', 'client', 'detective']
  phone: string?
  created_at: datetime
  updated_at: datetime
}
```

### Case Model
```
Case {
  id: string (UUID)
  title: string
  description: string?
  status: enum ['OPEN', 'IN_PROGRESS', 'REVIEW', 'CLOSED']
  owner_id: string (FK → User.id, lawyer)
  created_at: datetime
  updated_at: datetime
}
```

### CaseMember Model
```
CaseMember {
  id: int
  case_id: string (FK → Case.id)
  user_id: string (FK → User.id)
  role: enum ['OWNER', 'MEMBER', 'VIEWER', 'CLIENT']
  added_at: datetime
}
```

---

## Derived Views (No New Tables Required)

### ClientView (Derived)
Clients are users with `role='client'` linked to lawyer's cases.

```
ClientView {
  // From User
  id: string
  name: string
  email: string
  phone: string?

  // Computed
  case_count: int              # Number of cases with this lawyer
  linked_cases: CaseSummary[]  # Cases involving this client
  last_activity: datetime?     # Most recent case update
  created_at: datetime         # First case assignment date
}
```

**SQL Query:**
```sql
SELECT
  u.id, u.name, u.email, u.phone,
  COUNT(DISTINCT c.id) as case_count,
  MAX(c.updated_at) as last_activity
FROM users u
JOIN case_members cm ON u.id = cm.user_id
JOIN cases c ON cm.case_id = c.id
WHERE c.owner_id = :lawyer_id
  AND u.role = 'client'
GROUP BY u.id
```

### InvestigatorView (Derived)
Investigators/detectives assigned to lawyer's cases.

```
InvestigatorView {
  // From User
  id: string
  name: string
  email: string
  phone: string?

  // Computed
  specialization: string?      # From user metadata or profile
  active_assignments: int      # Open cases assigned
  completed_assignments: int   # Closed cases assigned
  availability: enum ['available', 'busy', 'unavailable']
  linked_cases: CaseSummary[]
  last_activity: datetime?
}
```

**SQL Query:**
```sql
SELECT
  u.id, u.name, u.email, u.phone,
  COUNT(DISTINCT CASE WHEN c.status != 'CLOSED' THEN c.id END) as active_assignments,
  COUNT(DISTINCT CASE WHEN c.status = 'CLOSED' THEN c.id END) as completed_assignments
FROM users u
JOIN case_members cm ON u.id = cm.user_id
JOIN cases c ON cm.case_id = c.id
WHERE c.owner_id = :lawyer_id
  AND u.role = 'detective'
GROUP BY u.id
```

---

## Settings Model (New or Extended)

### UserSettings (May Need New Table)
If not already in user profile:

```
UserSettings {
  user_id: string (PK, FK → User.id)

  // Profile
  display_name: string?
  avatar_url: string?
  timezone: string (default: 'Asia/Seoul')
  language: string (default: 'ko')

  // Notifications
  email_notifications: boolean (default: true)
  push_notifications: boolean (default: true)
  notification_frequency: enum ['immediate', 'daily', 'weekly']

  // Privacy
  profile_visibility: enum ['public', 'team', 'private']

  updated_at: datetime
}
```

**Implementation Note:** Check if these fields already exist in User model or need separate settings table.

---

## API Response Schemas

### ClientListResponse
```typescript
interface ClientListResponse {
  items: ClientItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface ClientItem {
  id: string;
  name: string;
  email: string;
  phone?: string;
  case_count: number;
  last_activity?: string; // ISO datetime
  status: 'active' | 'inactive'; // has open cases?
}
```

### InvestigatorListResponse
```typescript
interface InvestigatorListResponse {
  items: InvestigatorItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface InvestigatorItem {
  id: string;
  name: string;
  email: string;
  phone?: string;
  specialization?: string;
  active_assignments: number;
  completed_assignments: number;
  availability: 'available' | 'busy' | 'unavailable';
  last_activity?: string;
}
```

### UserSettingsResponse
```typescript
interface UserSettingsResponse {
  profile: {
    display_name: string;
    email: string;
    phone?: string;
    avatar_url?: string;
    timezone: string;
    language: string;
  };
  notifications: {
    email_enabled: boolean;
    push_enabled: boolean;
    frequency: 'immediate' | 'daily' | 'weekly';
  };
  security: {
    two_factor_enabled: boolean;
    last_password_change?: string;
  };
}
```

---

## Filter Parameters

### ClientFilter
```typescript
interface ClientFilter {
  search?: string;      // name or email
  status?: 'active' | 'inactive' | 'all';
  sort_by?: 'name' | 'case_count' | 'last_activity';
  sort_order?: 'asc' | 'desc';
}
```

### InvestigatorFilter
```typescript
interface InvestigatorFilter {
  search?: string;
  availability?: 'available' | 'busy' | 'unavailable' | 'all';
  sort_by?: 'name' | 'active_assignments' | 'last_activity';
  sort_order?: 'asc' | 'desc';
}
```

---

## Relationships Diagram

```
User (lawyer) ────owns────> Case
     │                        │
     │                        │
     └──────────────────> CaseMember <────────┐
                              │               │
                              │               │
                    User (client)      User (detective)
```

---

## Migration Notes

No database migrations required for core functionality:
- Client list: Query existing `users` + `case_members` + `cases` tables
- Investigator list: Query existing tables with role filter
- Settings: May need `user_settings` table if profile fields insufficient

Optional migration for UserSettings:
```sql
CREATE TABLE user_settings (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  display_name VARCHAR(100),
  timezone VARCHAR(50) DEFAULT 'Asia/Seoul',
  language VARCHAR(10) DEFAULT 'ko',
  email_notifications BOOLEAN DEFAULT TRUE,
  push_notifications BOOLEAN DEFAULT TRUE,
  notification_frequency VARCHAR(20) DEFAULT 'immediate',
  updated_at TIMESTAMP DEFAULT NOW()
);
```
