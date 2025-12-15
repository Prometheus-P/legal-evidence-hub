# Data Model: Authentication State

**Feature**: 011-production-bug-fixes
**Date**: 2025-12-11

## Overview

이 문서는 로그인 버그 수정에 관련된 인증 상태 엔티티들을 정의한다. 버그 수정 자체는 기존 엔티티를 변경하지 않으며, 상태 동기화 로직만 수정한다.

## Entities

### 1. User (Backend - PostgreSQL)

기존 사용자 모델. 버그 수정에서 변경 없음.

```python
class User(Base):
    __tablename__ = "users"

    id: str              # UUID, primary key
    email: str           # unique
    name: str
    role: UserRole       # LAWYER | CLIENT | DETECTIVE
    status: UserStatus   # ACTIVE | INACTIVE | PENDING
    hashed_password: str
    created_at: datetime
    updated_at: datetime
```

### 2. JWT Payload (Backend → Frontend)

JWT 토큰에 포함되는 클레임.

```typescript
interface JWTPayload {
  sub: string;           // user_id
  exp: number;           // expiration timestamp
  iat: number;           // issued at timestamp
  type?: "refresh";      // refresh 토큰만 해당
}
```

### 3. AuthUser (Frontend State)

프론트엔드에서 관리하는 사용자 상태.

```typescript
interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: "lawyer" | "client" | "detective";
  status: "active" | "inactive" | "pending";
}
```

### 4. AuthState (Frontend Context)

AuthContext에서 관리하는 전체 인증 상태.

```typescript
interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;  // computed: user !== null
}
```

## Storage Locations

| Data | Storage Type | Accessibility | Purpose |
|------|--------------|---------------|---------|
| `access_token` | HTTP-only Cookie | Backend only | API 인증 |
| `refresh_token` | HTTP-only Cookie (path=/auth) | Backend only | 토큰 갱신 |
| `user_data` | Public Cookie | Frontend + Middleware | 라우트 보호 |
| `USER_CACHE_KEY` | localStorage | Frontend only | Race condition 방지 |
| `JUST_LOGGED_IN_KEY` | sessionStorage | Frontend only | Race condition 플래그 |
| `AuthUser` | React Context | Frontend only | UI 렌더링 |

## State Transitions

### Login Flow

```
[Unauthenticated]
    │
    ▼ POST /auth/login (success)
    │
[Cookies Set by Backend]
    │
    ▼ Frontend: Set localStorage + sessionStorage
    │
[Authenticated + JUST_LOGGED_IN flag]
    │
    ▼ router.push(dashboard)
    │
[New Page Mount]
    │
    ▼ AuthProvider: Check JUST_LOGGED_IN
    │
    ├─── true: Load from localStorage, clear flag
    │          → [Authenticated (from cache)]
    │
    └─── false: Call GET /auth/me
               ├─── success: [Authenticated]
               └─── failure: [Unauthenticated]
```

### Logout Flow

```
[Authenticated]
    │
    ▼ POST /auth/logout
    │
[Backend: Clear cookies]
    │
    ▼ Frontend: Clear all storage
    │
[Unauthenticated]
```

## Cookie Configuration

### access_token (HTTP-only)

```
Set-Cookie: access_token=<jwt>;
  HttpOnly;
  Secure;
  SameSite=None;
  Path=/;
  Max-Age=86400
```

### refresh_token (HTTP-only)

```
Set-Cookie: refresh_token=<jwt>;
  HttpOnly;
  Secure;
  SameSite=None;
  Path=/auth;
  Max-Age=604800
```

### user_data (Public)

```
Set-Cookie: user_data=<encoded_json>;
  Path=/;
  Max-Age=86400
```

**Note**: `SameSite=None`은 cross-origin 환경 (CloudFront ↔ API)에서 필수. `Secure=true`와 함께 사용해야 함.

## Validation Rules

| Field | Rule |
|-------|------|
| JWT `exp` | 현재 시간보다 미래여야 함 |
| JWT `sub` | 유효한 user_id (DB에 존재) |
| User `role` | "lawyer" \| "client" \| "detective" 중 하나 |
| User `status` | "active"만 로그인 허용 |

## Role-based Dashboard Mapping

```typescript
const DASHBOARD_PATHS: Record<UserRole, string> = {
  lawyer: "/lawyer/dashboard",
  client: "/client/dashboard",
  detective: "/detective/dashboard",
};
```

## Changes Required for Bug Fix

이 버그 수정은 데이터 모델 자체를 변경하지 않음. 변경 대상:

1. **Cookie Configuration**: SameSite, Secure 설정 검증/수정
2. **State Sync Logic**: localStorage/sessionStorage 저장 순서
3. **Middleware Logic**: user_data 쿠키 파싱 및 리다이렉트

---

# Data Model: Lawyer Portal Features (US2)

**Date**: 2025-12-12

## New Entities

### 5. Notification (Backend - PostgreSQL)

알림 정보를 저장하는 테이블.

```python
class NotificationType(str, Enum):
    CASE_UPDATE = "case_update"   # 사건 관련 업데이트
    MESSAGE = "message"           # 새 메시지 도착
    SYSTEM = "system"             # 시스템 공지

class Notification(Base):
    __tablename__ = "notifications"

    id: str                       # UUID, primary key
    user_id: str                  # FK → users.id (알림 수신자)
    type: NotificationType        # 알림 유형
    title: str                    # 알림 제목 (최대 100자)
    content: str                  # 알림 내용 (최대 500자)
    is_read: bool = False         # 읽음 여부
    related_id: str | None        # 관련 엔티티 ID (case_id, message_id 등)
    created_at: datetime
```

**Validation Rules**:
- `title`: 1~100자
- `content`: 1~500자
- `type`: NotificationType enum 값만 허용

### 6. Message (Backend - PostgreSQL)

메시지 정보를 저장하는 테이블.

```python
class Message(Base):
    __tablename__ = "messages"

    id: str                       # UUID, primary key
    sender_id: str                # FK → users.id (발신자)
    recipient_id: str             # FK → users.id (수신자)
    subject: str                  # 제목 (최대 200자)
    content: str                  # 내용 (텍스트)
    is_read: bool = False         # 읽음 여부
    is_deleted_by_sender: bool = False     # 발신자 삭제
    is_deleted_by_recipient: bool = False  # 수신자 삭제
    created_at: datetime
    read_at: datetime | None      # 읽은 시각
```

**Validation Rules**:
- `subject`: 1~200자
- `content`: 1자 이상 (최대 길이 없음)
- 삭제는 soft delete (각 사용자별)

### 7. Client (Backend - PostgreSQL)

의뢰인(연락처) 정보를 저장하는 테이블. User와 별도로 관리.

```python
class Client(Base):
    __tablename__ = "clients"

    id: str                       # UUID, primary key
    lawyer_id: str                # FK → users.id (담당 변호사)
    name: str                     # 의뢰인 이름
    phone: str | None             # 전화번호
    email: str | None             # 이메일
    memo: str | None              # 메모 (선택)
    created_at: datetime
    updated_at: datetime
```

**Validation Rules**:
- `name`: 1~100자, 필수
- `phone`: 한국 전화번호 형식 (010-XXXX-XXXX 또는 유사), 선택
- `email`: 이메일 형식, 선택
- `phone` 또는 `email` 중 하나는 필수

### 8. Detective (Backend - PostgreSQL)

탐정(연락처) 정보를 저장하는 테이블.

```python
class Detective(Base):
    __tablename__ = "detectives"

    id: str                       # UUID, primary key
    lawyer_id: str                # FK → users.id (담당 변호사)
    name: str                     # 탐정 이름
    phone: str | None             # 전화번호
    email: str | None             # 이메일
    specialty: str | None         # 전문 분야 (예: 불륜 조사, 자산 추적)
    memo: str | None              # 메모 (선택)
    created_at: datetime
    updated_at: datetime
```

**Validation Rules**:
- `name`: 1~100자, 필수
- `phone`: 한국 전화번호 형식, 선택
- `email`: 이메일 형식, 선택
- `phone` 또는 `email` 중 하나는 필수

## Frontend Types

### NotificationDTO

```typescript
interface Notification {
  id: string;
  type: "case_update" | "message" | "system";
  title: string;
  content: string;
  isRead: boolean;
  relatedId?: string;
  createdAt: string;  // ISO 8601
}
```

### MessageDTO

```typescript
interface Message {
  id: string;
  senderId: string;
  senderName: string;
  recipientId: string;
  recipientName: string;
  subject: string;
  content: string;
  isRead: boolean;
  createdAt: string;
  readAt?: string;
}

interface MessageCreate {
  recipientId: string;
  subject: string;
  content: string;
}
```

### ClientDTO

```typescript
interface Client {
  id: string;
  name: string;
  phone?: string;
  email?: string;
  memo?: string;
  createdAt: string;
  updatedAt: string;
}

interface ClientCreate {
  name: string;
  phone?: string;
  email?: string;
  memo?: string;
}
```

### DetectiveDTO

```typescript
interface Detective {
  id: string;
  name: string;
  phone?: string;
  email?: string;
  specialty?: string;
  memo?: string;
  createdAt: string;
  updatedAt: string;
}

interface DetectiveCreate {
  name: string;
  phone?: string;
  email?: string;
  specialty?: string;
  memo?: string;
}
```

## Entity Relationships

```
┌─────────┐      1:N      ┌──────────────┐
│  User   │──────────────▶│ Notification │
└─────────┘               └──────────────┘
     │
     │ 1:N (sender)
     ▼
┌─────────┐      1:N      ┌─────────────┐
│  User   │──────────────▶│   Message   │
└─────────┘ (recipient)   └─────────────┘
     │
     │ 1:N (lawyer)
     ▼
┌─────────┐               ┌─────────────┐
│  User   │──────────────▶│   Client    │
└─────────┘               └─────────────┘
     │
     │ 1:N (lawyer)
     ▼
┌─────────┐               ┌─────────────┐
│  User   │──────────────▶│  Detective  │
└─────────┘               └─────────────┘
```

## State Transitions

### Notification State

```
[Created (is_read=false)]
    │
    ▼ User views notification
    │
[Read (is_read=true)]
```

### Message State

```
[Created (is_read=false)]
    │
    ├──▶ Recipient reads → [Read (is_read=true, read_at set)]
    │
    ├──▶ Sender deletes → [is_deleted_by_sender=true]
    │
    └──▶ Recipient deletes → [is_deleted_by_recipient=true]

Note: Both flags true → soft deleted (excluded from queries)
```

## Migration Notes

```sql
-- Notification
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR(20) NOT NULL,
    title VARCHAR(100) NOT NULL,
    content VARCHAR(500) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Message
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES users(id),
    recipient_id UUID NOT NULL REFERENCES users(id),
    subject VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    is_deleted_by_sender BOOLEAN DEFAULT FALSE,
    is_deleted_by_recipient BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP
);

-- Client
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lawyer_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Detective
CREATE TABLE detectives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lawyer_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    specialty VARCHAR(100),
    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```
