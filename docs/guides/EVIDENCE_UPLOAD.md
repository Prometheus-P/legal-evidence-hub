# Evidence Upload Guide

> S3 증거 파일 업로드 패턴 및 AI Worker 연동 가이드

---

## 1. S3 Path 구조

### 기본 패턴

```
cases/{case_id}/raw/{evidence_id}_{filename}
```

| 세그먼트 | 설명 | 예시 |
|----------|------|------|
| `cases/` | 고정 prefix | - |
| `{case_id}` | 사건 고유 ID | `case_001`, `cs_abc123` |
| `raw/` | 원본 파일 디렉토리 | - |
| `{evidence_id}` | 증거 고유 ID (Backend 생성) | `ev_abc123` |
| `{filename}` | 원본 파일명 | `photo.jpg`, `chat.txt` |

### 예시

```
cases/case_001/raw/ev_abc123_photo.jpg
cases/case_001/raw/ev_def456_kakaotalk_export.txt
cases/cs_xyz789/raw/ev_ghi012_recording.mp3
```

---

## 2. 업로드 흐름

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│     S3      │────▶│  AI Worker  │
│  (Upload)   │     │ (Pre-sign)  │     │  (Storage)  │     │  (Lambda)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Step 1: Frontend → Backend
- 사용자가 증거 파일 선택
- Backend에 presigned URL 요청

### Step 2: Backend
- `evidence_id` 생성 (예: `ev_abc123`)
- DynamoDB에 증거 레코드 생성 (status: `pending`)
- S3 presigned URL 생성 및 반환

### Step 3: Frontend → S3
- Presigned URL로 직접 S3 업로드
- 파일 경로: `cases/{case_id}/raw/{evidence_id}_{filename}`

### Step 4: S3 → AI Worker (Lambda)
- S3 ObjectCreated 이벤트 트리거
- Lambda가 파일 처리 시작

---

## 3. 지원 파일 형식

| 카테고리 | 확장자 | Parser |
|----------|--------|--------|
| **텍스트** | `.txt`, `.csv`, `.json` | TextParser (KakaoTalk 자동 감지) |
| **이미지** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp` | ImageVisionParser (GPT-4V OCR) |
| **PDF** | `.pdf` | PDFParser |
| **오디오** | `.mp3`, `.wav`, `.m4a`, `.aac` | AudioParser (Whisper STT) |
| **비디오** | `.mp4`, `.avi`, `.mov`, `.mkv` | VideoParser |

---

## 4. 파일명 규칙

### 권장사항

```
✅ ev_abc123_photo.jpg
✅ ev_def456_kakaotalk_2024.txt
✅ ev_ghi789_contract_scan.pdf
```

### 금지사항

```
❌ photo (1).jpg          # 특수문자 포함
❌ 사진.jpg               # 한글 파일명 (인코딩 이슈)
❌ my file name.txt       # 공백 포함
❌ ../../../etc/passwd    # 경로 탐색 시도
```

### 파일명 정규화

Backend에서 업로드 전 파일명 정규화:
- 공백 → 언더스코어 (`_`)
- 특수문자 제거
- 한글 → 영문 또는 제거
- 최대 길이 제한 (100자)

---

## 5. 파일 크기 제한

| 파일 타입 | 최대 크기 | 비고 |
|-----------|-----------|------|
| 텍스트 | 10 MB | - |
| 이미지 | 20 MB | - |
| PDF | 50 MB | - |
| 오디오 | 100 MB | 10분 이하 권장 |
| 비디오 | 500 MB | 5분 이하 권장 |

> 초과 시 AI Worker에서 `FileSizeExceeded` 에러 반환

---

## 6. AWS CLI 테스트

### 직접 업로드 (테스트용)

```bash
# 환경 변수 설정
export BUCKET=leh-evidence-dev
export CASE_ID=case_test_001
export EVIDENCE_ID=ev_test_$(date +%s)

# 파일 업로드
aws s3 cp ./test_file.txt \
  s3://$BUCKET/cases/$CASE_ID/raw/${EVIDENCE_ID}_test_file.txt

# 업로드 확인
aws s3 ls s3://$BUCKET/cases/$CASE_ID/raw/
```

### Lambda 트리거 확인

```bash
# CloudWatch 로그 확인
aws logs tail /aws/lambda/leh-ai-worker --follow
```

---

## 7. 멱등성 (Idempotency)

AI Worker는 중복 처리를 방지합니다:

| 체크 | 설명 |
|------|------|
| **evidence_id** | 이미 처리된 증거 ID면 skip |
| **file_hash** | 동일 파일 해시면 skip |
| **s3_key** | 동일 S3 경로면 skip |

### 응답 예시 (중복)

```json
{
  "status": "skipped",
  "reason": "already_processed_evidence_id",
  "evidence_id": "ev_abc123"
}
```

---

## 8. 에러 처리

| 에러 타입 | 원인 | 해결 |
|-----------|------|------|
| `VALIDATION_ERROR` | 지원하지 않는 파일 형식 | 파일 확장자 확인 |
| `FileSizeExceeded` | 파일 크기 초과 | 파일 압축 또는 분할 |
| `PARSE_ERROR` | 파일 파싱 실패 | 파일 손상 확인 |
| `API_ERROR` | OpenAI/Qdrant 오류 | 재시도 또는 관리자 문의 |

---

## 9. Qdrant 컬렉션 구조

처리된 증거는 Qdrant에 벡터로 저장됩니다:

```
컬렉션명: case_rag_{case_id}
예: case_rag_case_001
```

### 메타데이터

```json
{
  "chunk_id": "chunk_abc123",
  "file_id": "ev_abc123",
  "case_id": "case_001",
  "content": "대화 내용...",
  "timestamp": "2024-01-15T10:30:00Z",
  "sender": "홍길동",
  "file_name": "kakaotalk.txt",
  "file_type": "kakaotalk",
  "legal_categories": ["AFFAIR", "VIOLENCE"],
  "confidence_level": 0.85
}
```

---

## 10. 관련 문서

- [AI Worker Pattern Guide](./AI_WORKER_PATTERN_GUIDE.md)
- [Backend Service Repository Guide](./BACKEND_SERVICE_REPOSITORY_GUIDE.md)
- [Testing Strategy](./TESTING_STRATEGY.md)
