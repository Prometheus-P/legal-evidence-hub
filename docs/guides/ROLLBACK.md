# Rollback Procedure Guide

> LEH 서비스 롤백 절차 가이드

## 1. 개요

이 문서는 LEH 서비스 배포 후 문제가 발생했을 때 이전 버전으로 롤백하는 절차를 설명합니다.

---

## 2. 롤백 시나리오

| 시나리오 | 증상 | 긴급도 |
|----------|------|--------|
| Frontend 오류 | 페이지 로딩 실패, JS 에러 | 높음 |
| Backend API 실패 | 500 에러, 응답 없음 | 높음 |
| AI Worker 실패 | 증거 분석 중단 | 중간 |
| 데이터베이스 마이그레이션 실패 | 쿼리 에러 | 높음 |

---

## 3. Frontend 롤백 (CloudFront + S3)

### 3.1 이전 버전 확인

```bash
# S3 버킷 버전 히스토리 확인
aws s3api list-object-versions \
  --bucket leh-frontend-prod \
  --prefix index.html \
  --max-items 5
```

### 3.2 CloudFront 캐시 무효화

```bash
# 캐시 무효화 생성
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
  --paths "/*"

# 무효화 상태 확인
aws cloudfront get-invalidation \
  --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
  --id $INVALIDATION_ID
```

### 3.3 이전 빌드로 롤백

```bash
# 1. 이전 커밋으로 체크아웃
git checkout $PREVIOUS_COMMIT_SHA

# 2. 프론트엔드 빌드
cd frontend
npm ci
npm run build

# 3. S3에 재배포
aws s3 sync out/ s3://leh-frontend-prod/ --delete

# 4. CloudFront 캐시 무효화
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
  --paths "/*"
```

---

## 4. Backend 롤백 (ECR + ECS/Lambda)

### 4.1 ECR 이미지 태그 확인

```bash
# 최근 이미지 태그 확인
aws ecr describe-images \
  --repository-name leh-backend \
  --query 'imageDetails[*].[imageTags,imagePushedAt]' \
  --output table \
  | head -10
```

### 4.2 이전 이미지로 롤백 (ECS)

```bash
# 1. 이전 이미지 태그로 태스크 정의 업데이트
aws ecs update-service \
  --cluster leh-cluster \
  --service leh-backend \
  --force-new-deployment \
  --task-definition leh-backend:$PREVIOUS_REVISION

# 2. 배포 상태 확인
aws ecs describe-services \
  --cluster leh-cluster \
  --services leh-backend \
  --query 'services[0].deployments'
```

### 4.3 이전 이미지로 롤백 (Lambda)

```bash
# Lambda 함수 이미지 업데이트
aws lambda update-function-code \
  --function-name leh-ai-worker \
  --image-uri $ECR_REGISTRY/leh-ai-worker:$PREVIOUS_TAG
```

---

## 5. Database 롤백 (Alembic)

### 5.1 현재 마이그레이션 상태 확인

```bash
cd backend
alembic current
alembic history --verbose | head -20
```

### 5.2 이전 마이그레이션으로 롤백

```bash
# 1개 마이그레이션 롤백
alembic downgrade -1

# 특정 리비전으로 롤백
alembic downgrade $REVISION_ID

# 모든 마이그레이션 롤백 (주의!)
alembic downgrade base
```

### 5.3 롤백 후 확인

```bash
# 현재 상태 확인
alembic current

# 테이블 상태 확인
psql $DATABASE_URL -c "\dt"
```

---

## 6. GitHub Actions 워크플로우 롤백

### 6.1 이전 성공 빌드 재실행

1. GitHub Actions 페이지로 이동
2. 마지막 성공 워크플로우 선택
3. "Re-run all jobs" 클릭

### 6.2 특정 커밋으로 배포

```bash
# 1. 로컬에서 특정 커밋 체크아웃
git checkout $STABLE_COMMIT_SHA

# 2. 새 브랜치 생성
git checkout -b hotfix/rollback-$DATE

# 3. dev 브랜치로 강제 푸시 (주의!)
git push origin hotfix/rollback-$DATE:dev --force
```

---

## 7. 롤백 체크리스트

### 7.1 롤백 전
- [ ] 현재 문제 증상 기록
- [ ] 롤백 대상 버전/커밋 확인
- [ ] 팀원에게 롤백 공지
- [ ] 롤백 시간 예상

### 7.2 롤백 중
- [ ] 서비스 모니터링 (CloudWatch, 로그)
- [ ] 롤백 명령 실행
- [ ] 배포 상태 확인

### 7.3 롤백 후
- [ ] 서비스 정상 작동 확인
- [ ] 기능 테스트 수행
- [ ] 롤백 결과 팀에 공유
- [ ] 원인 분석 및 문서화

---

## 8. 긴급 연락처

| 역할 | 담당 | 책임 영역 |
|------|------|-----------|
| Frontend/PM | P | CloudFront, S3, Next.js |
| Backend/Infra | H | ECS, RDS, API |
| AI/Data | L | Lambda, DynamoDB, Qdrant |

---

## 9. 관련 문서

- [배포 가이드](../specs/ARCHITECTURE.md)
- [CI/CD 워크플로우](.github/workflows/)
- [환경 변수 설정](../ENVIRONMENT.md)
