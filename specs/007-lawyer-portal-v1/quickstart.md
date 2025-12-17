# LEH Lawyer Portal v1 Quick Start Guide

**Feature Branch**: `feat/007-lawyer-portal-v1`
**Version**: v1.0
**Last Updated**: 2025-12-08

---

## 1. Prerequisites

### 1.1 Environment Setup

```bash
# Clone and checkout feature branch
git fetch origin
git checkout feat/007-lawyer-portal-v1

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 1.2 Required Dependencies

**Backend (Python)**:
- All existing requirements
- No new packages needed for Phase 1

**Frontend (npm)**:
```bash
npm install @xyflow/react@^12.0.0
npm install xlsx@^0.18.5  # Optional: for Asset Sheet export
```

### 1.3 Database

Ensure PostgreSQL is running and configured in `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/leh_dev
```

---

## 2. Quick Implementation Steps

### Phase 1: Party Relationship Graph (MVP)

#### Step 1: Database Migration

```bash
cd backend

# Create migration files
alembic revision --autogenerate -m "add_party_nodes"
alembic revision --autogenerate -m "add_party_relationships"  
alembic revision --autogenerate -m "add_evidence_party_links"

# Apply migrations
alembic upgrade head
```

#### Step 2: Backend Implementation

**File structure to create:**
```
backend/app/
├── db/models/
│   ├── party_node.py
│   ├── party_relationship.py
│   └── evidence_party_link.py
├── schemas/
│   └── party.py
├── repositories/
│   └── party_repository.py
├── services/
│   └── party_service.py
└── api/
    └── party.py
```

**Register routes in main.py:**
```python
# backend/app/main.py
from app.api import party

app.include_router(party.router, prefix="/api/v1", tags=["Parties"])
```

#### Step 3: Run Backend Tests

```bash
cd backend
pytest tests/test_api/test_party.py -v
```

#### Step 4: Frontend Implementation

**File structure to create:**
```
frontend/src/
├── components/party/
│   ├── PartyGraph.tsx
│   ├── PartyNode.tsx
│   ├── PartyEdge.tsx
│   ├── PartyModal.tsx
│   └── RelationshipModal.tsx
├── hooks/
│   ├── usePartyGraph.ts
│   └── useAutoSave.ts
├── lib/api/
│   └── party.ts
└── types/
    └── party.ts
```

#### Step 5: Add Tab to Case Detail Page

```typescript
// frontend/src/app/lawyer/cases/[id]/page.tsx
// Add to tabs array:
{ id: 'graph', label: '관계도', component: PartyGraph }
```

#### Step 6: Run Frontend Tests

```bash
cd frontend
npm test -- --testPathPattern=party
```

---

## 3. Key Code Snippets

### 3.1 SQLAlchemy Model (party_node.py)

```python
from sqlalchemy import Column, String, Integer, Float, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class PartyType(str, Enum):
    PLAINTIFF = "plaintiff"
    DEFENDANT = "defendant"
    THIRD_PARTY = "third_party"
    CHILD = "child"
    FAMILY = "family"

class PartyNode(Base):
    __tablename__ = "party_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    alias = Column(String(50))
    birth_year = Column(Integer)
    occupation = Column(String(100))
    position_x = Column(Float, default=0)
    position_y = Column(Float, default=0)
    metadata = Column(JSONB, default={})
    
    # Relationships
    case = relationship("Case", back_populates="party_nodes")
    source_relationships = relationship("PartyRelationship", foreign_keys="PartyRelationship.source_party_id")
    target_relationships = relationship("PartyRelationship", foreign_keys="PartyRelationship.target_party_id")
```

### 3.2 API Router (party.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, get_current_user_id, verify_case_access
from app.schemas.party import PartyNodeCreate, PartyNodeUpdate, PartyNodeResponse
from app.services.party_service import PartyService

router = APIRouter()

@router.get("/cases/{case_id}/parties", response_model=dict)
async def get_parties(
    case_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    await verify_case_access(case_id, user_id, db)
    service = PartyService(db)
    parties = service.get_parties_by_case(case_id)
    return {"items": parties, "total": len(parties)}

@router.post("/cases/{case_id}/parties", response_model=PartyNodeResponse, status_code=201)
async def create_party(
    case_id: str,
    party: PartyNodeCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    await verify_case_write_access(case_id, user_id, db)
    service = PartyService(db)
    return service.create_party(case_id, party)
```

### 3.3 React Flow Setup (PartyGraph.tsx)

```typescript
'use client';

import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Node,
  Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { usePartyGraph } from '@/hooks/usePartyGraph';
import { PlaintiffNode, DefendantNode, ThirdPartyNode, ChildNode, FamilyNode } from './nodes';
import { MarriageEdge, AffairEdge, FamilyEdge } from './edges';

const nodeTypes = {
  plaintiff: PlaintiffNode,
  defendant: DefendantNode,
  third_party: ThirdPartyNode,
  child: ChildNode,
  family: FamilyNode,
};

const edgeTypes = {
  marriage: MarriageEdge,
  affair: AffairEdge,
  parent_child: FamilyEdge,
  sibling: FamilyEdge,
  in_law: FamilyEdge,
  cohabit: FamilyEdge,
};

interface PartyGraphProps {
  caseId: string;
}

export function PartyGraph({ caseId }: PartyGraphProps) {
  const { data, isLoading, savePositions } = usePartyGraph(caseId);

  const initialNodes = useMemo(() => 
    data?.nodes.map(party => ({
      id: party.id,
      type: party.type,
      position: party.position,
      data: { label: party.name, party },
    })) ?? [], 
    [data?.nodes]
  );

  const initialEdges = useMemo(() =>
    data?.relationships.map(rel => ({
      id: rel.id,
      source: rel.source_party_id,
      target: rel.target_party_id,
      type: rel.type,
      data: { relationship: rel },
    })) ?? [],
    [data?.relationships]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((connection: Connection) => {
    // Open relationship modal for new connection
    setEdges((eds) => addEdge(connection, eds));
  }, [setEdges]);

  const onNodeDragStop = useCallback((event: React.MouseEvent, node: Node) => {
    savePositions([{ id: node.id, position: node.position }]);
  }, [savePositions]);

  if (isLoading) {
    return <div className="h-[600px] animate-pulse bg-gray-100" />;
  }

  if (!data?.nodes.length) {
    return (
      <div className="h-[600px] flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 mb-4">관계도가 비어 있습니다</p>
          <p className="text-sm text-gray-400 mb-4">당사자를 추가하여 관계도를 시작하세요.</p>
          <button className="px-4 py-2 bg-primary text-white rounded">
            + 원고/피고 추가하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[600px]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStop={onNodeDragStop}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
```

### 3.4 Auto-Save Hook (useAutoSave.ts)

```typescript
import { useCallback, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';

interface UseAutoSaveOptions<T> {
  saveFn: (data: T) => Promise<void>;
  debounceMs?: number;
  onSaveStart?: () => void;
  onSaveSuccess?: () => void;
  onSaveError?: (error: Error) => void;
}

export function useAutoSave<T>({
  saveFn,
  debounceMs = 2500,
  onSaveStart,
  onSaveSuccess,
  onSaveError,
}: UseAutoSaveOptions<T>) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pendingDataRef = useRef<T | null>(null);

  const mutation = useMutation({
    mutationFn: saveFn,
    onMutate: onSaveStart,
    onSuccess: onSaveSuccess,
    onError: onSaveError,
  });

  const scheduleSave = useCallback((data: T) => {
    pendingDataRef.current = data;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      if (pendingDataRef.current) {
        mutation.mutate(pendingDataRef.current);
        pendingDataRef.current = null;
      }
    }, debounceMs);
  }, [debounceMs, mutation]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    scheduleSave,
    isSaving: mutation.isPending,
    saveError: mutation.error,
    isError: mutation.isError,
  };
}
```

---

## 4. Testing Checklist

### 4.1 Backend Tests

```bash
# Run all party tests
pytest tests/test_api/test_party.py -v

# Run with coverage
pytest tests/test_api/test_party.py --cov=app/services/party_service --cov-report=term-missing
```

**Test cases to implement:**
- [ ] `test_get_parties_empty_case` - Returns empty list for new case
- [ ] `test_create_party_plaintiff` - Creates plaintiff node
- [ ] `test_create_party_defendant` - Creates defendant node
- [ ] `test_update_party_position` - Updates node position
- [ ] `test_delete_party_cascades_relationships` - Deletes related relationships
- [ ] `test_create_relationship` - Creates relationship between parties
- [ ] `test_create_relationship_self_reference_fails` - Prevents self-reference
- [ ] `test_viewer_cannot_modify` - VIEWER role cannot create/update/delete

### 4.2 Frontend Tests

```bash
# Run party component tests
npm test -- --testPathPattern=party

# Run with coverage
npm test -- --testPathPattern=party --coverage
```

**Test cases to implement:**
- [ ] `PartyGraph renders empty state when no parties`
- [ ] `PartyGraph renders nodes for each party`
- [ ] `PartyGraph calls savePositions on node drag`
- [ ] `PartyModal validates required fields`
- [ ] `RelationshipModal prevents self-reference`

### 4.3 E2E Tests

```bash
# Run Playwright tests
npm run test:e2e -- --grep "party"
```

**E2E scenarios:**
- [ ] US1-1: Navigate to 관계도 tab, see React Flow canvas
- [ ] US1-2: Click 당사자 추가, fill form, see new node
- [ ] US1-3: Drag between nodes, create relationship
- [ ] US1-5: Edit node, see 저장됨 toast after 3 seconds

---

## 5. Deployment Checklist

### 5.1 Pre-deployment

- [ ] All backend tests passing
- [ ] All frontend tests passing
- [ ] E2E tests passing
- [ ] Feature flag set: `FEATURES.PARTY_GRAPH = true`
- [ ] Database migrations created and tested locally

### 5.2 Deployment Steps

```bash
# 1. Deploy database migration first
alembic upgrade head

# 2. Deploy backend
# (your deployment process)

# 3. Deploy frontend
# (your deployment process)

# 4. Verify in staging
# - Check /lawyer/cases/{id} loads 관계도 tab
# - Test CRUD operations
# - Test auto-save functionality
```

### 5.3 Rollback Plan

```bash
# If issues occur:
# 1. Disable feature flag (immediate)
FEATURES.PARTY_GRAPH = false

# 2. If data issues, rollback migrations
alembic downgrade -3  # Rollback 3 migrations
```

---

## 6. Common Issues & Solutions

### Issue 1: React Flow not rendering

**Symptom**: Blank canvas, no nodes visible

**Solution**:
```typescript
// Ensure fitView is enabled and nodes have valid positions
<ReactFlow
  nodes={nodes}
  fitView
  defaultViewport={{ x: 0, y: 0, zoom: 1 }}
/>
```

### Issue 2: Positions not saving

**Symptom**: Node positions reset after page reload

**Solution**:
```typescript
// Ensure onNodeDragStop is calling API
const onNodeDragStop = useCallback((event, node) => {
  console.log('Saving position:', node.id, node.position);
  savePositions([{ id: node.id, position: node.position }]);
}, [savePositions]);
```

### Issue 3: 403 Forbidden on API calls

**Symptom**: All party API calls return 403

**Solution**:
- Verify user is a member of the case (`case_members` table)
- Check JWT token is valid and included in headers
- Ensure case_id in URL matches user's accessible cases

---

## 7. Reference Links

- **Spec Document**: [spec.md](./spec.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research Notes**: [research.md](./research.md)
- **API Contracts**: [contracts/](./contracts/)
- **React Flow Docs**: https://reactflow.dev/
- **Korean Civil Code 840**: https://www.law.go.kr/법령/민법/제840조

---

**END OF QUICKSTART.md**
