# Implementation Plan: 비동기 초안 생성 API 503 에러 해결

**Branch**: `015-fix-async-draft-503` | **Date**: 2025-12-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/015-fix-async-draft-503/spec.md`

## Summary

비동기 초안 생성 API (`POST /api/cases/{case_id}/draft-preview-async`)에서 브라우저 호출 시 503 에러 (또는 HTML 반환)가 발생하는 문제를 해결합니다.

**근본 원인**: CloudFront의 `CustomErrorResponses` 설정이 `/api/*` 경로의 403/404 에러를 `/index.html`로 리디렉트하여 HTML을 반환함.

## 원인 분석 결과

### 문제 재현 테스트

| 테스트 케이스 | 결과 | 설명 |
|--------------|------|------|
| 권한 있는 케이스로 POST | ✅ 성공 | `job_id` 정상 반환 |
| 권한 없는 케이스로 POST | ❌ 실패 | HTML 반환 (HTTP 200) |
| /api/health GET | ✅ 성공 | JSON 정상 반환 |
| 권한 없는 케이스로 GET | ❌ 실패 | HTML 반환 (HTTP 200) |

### 근본 원인 분석

**CloudFront 설정 (Distribution ID: E2ZX184AQP0EL5)**:

```json
"CustomErrorResponses": {
  "Items": [
    {
      "ErrorCode": 403,
      "ResponsePagePath": "/index.html",
      "ResponseCode": "200"
    },
    {
      "ErrorCode": 404,
      "ResponsePagePath": "/index.html",
      "ResponseCode": "200"
    }
  ]
}
```

**문제 흐름**:
1. 사용자가 권한 없는 케이스에 접근
2. Backend(Lambda)가 403 Forbidden 반환
3. CloudFront가 403을 감지하고 `/index.html`로 대체
4. 클라이언트는 HTTP 200 + HTML을 받음
5. JSON 파싱 실패 → 503 에러로 표시

**이것이 브라우저에서만 실패하는 이유**:
- curl 테스트 시에는 권한이 있는 케이스를 사용
- 브라우저에서는 다른 사용자가 소유한 케이스에 접근 시도

## Technical Context

**Language/Version**: AWS CloudFront 설정 + Python 3.11 (Backend)
**Primary Dependencies**: AWS CloudFront, API Gateway, Lambda
**Storage**: N/A (설정 변경만 필요)
**Testing**: curl, 브라우저 테스트
**Target Platform**: AWS CloudFront
**Project Type**: Infrastructure 설정 변경

## 해결 방안

### 옵션 1: CloudFront 에러 페이지 설정 제거 (권장)

CloudFront의 `CustomErrorResponses`에서 403/404 에러 페이지 리디렉트를 제거합니다.

**장점**:
- 근본적인 해결
- API 에러가 올바르게 전달됨
- SPA 라우팅은 S3 버킷 설정이나 Lambda@Edge로 처리 가능

**단점**:
- SPA 클라이언트 사이드 라우팅이 깨질 수 있음 (별도 처리 필요)

**구현**:
```bash
# 1. 현재 CloudFront 설정 백업
aws cloudfront get-distribution-config --id E2ZX184AQP0EL5 > cf-backup.json

# 2. CustomErrorResponses 제거하여 업데이트
# ETag 값 필요
```

### 옵션 2: S3 오리진에 에러 페이지 처리 위임

S3 버킷의 정적 웹사이트 호스팅에서 에러 페이지를 처리하도록 변경합니다.

**구현**:
1. CloudFront의 CustomErrorResponses 제거
2. S3 버킷에 에러 문서 설정: `index.html`
3. `/api/*` 경로는 API Gateway로 직접 전달되므로 영향 없음

### 옵션 3: CloudFront Function 사용

`/api/*` 요청에 대해 에러 응답을 가로채지 않도록 CloudFront Function을 추가합니다.

**단점**:
- 복잡성 증가
- 비용 발생

## 선택 방안

**옵션 1 (CloudFront 에러 페이지 제거)** 권장

이유:
1. SPA 라우팅은 이미 `/api/*`를 제외한 경로에서만 필요
2. CloudFront의 `/api/*` 캐시 동작은 에러 페이지 설정과 독립적으로 작동해야 함
3. Frontend는 Next.js SSR이므로 클라이언트 사이드 라우팅 의존도가 낮음

## 구현 단계

### Phase 1: CloudFront 설정 수정

1. **백업**: 현재 CloudFront 설정 저장
2. **수정**: CustomErrorResponses 제거 또는 수정
3. **배포**: CloudFront 배포 업데이트
4. **캐시 무효화**: 필요시 캐시 무효화

### Phase 2: 테스트

1. 권한 없는 케이스 접근 시 403 반환 확인
2. 권한 있는 케이스로 초안 생성 성공 확인
3. Frontend SPA 라우팅 정상 작동 확인
4. /api/health 등 기존 API 정상 작동 확인

## 위험 요소

| 위험 | 영향 | 완화 방안 |
|------|------|----------|
| SPA 라우팅 깨짐 | 사용자가 직접 URL 입력 시 404 | Next.js SSR이므로 영향 적음 |
| 기존 에러 처리 변경 | 사용자 경험 변화 | Frontend 에러 핸들링 검토 |

## 참고 자료

- [AWS CloudFront Custom Error Responses](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GeneratingCustomErrorResponses.html)
- [SPA Routing with CloudFront](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/SPAs.html)

## CloudFront 설정 정보

- **Distribution ID**: E2ZX184AQP0EL5
- **Domain**: dpbf86zqulqfy.cloudfront.net
- **Origins**:
  - `api-gateway`: zhfiuntwj0.execute-api.ap-northeast-2.amazonaws.com
  - `s3-frontend`: leh-frontend-prod.s3.ap-northeast-2.amazonaws.com

---

## 해결 완료 (2025-12-22)

### 적용된 변경사항

#### 1. CloudFront CustomErrorResponses 제거

`CustomErrorResponses`를 제거하여 API 에러가 올바르게 클라이언트에 전달되도록 수정했습니다.

```bash
# 명령어
aws cloudfront update-distribution --id E2ZX184AQP0EL5 \
  --if-match E2PK47MO2XV7S6 \
  --distribution-config file://cloudfront-update.json
```

**변경 전**: 403/404 에러 → `/index.html` (HTTP 200)
**변경 후**: 403/404 에러 → 원본 API 응답 (올바른 HTTP 상태 코드 + JSON)

#### 2. CloudFront Function 수정 (leh-url-rewrite)

SPA 동적 라우팅을 지원하기 위해 CloudFront Function을 업데이트했습니다.

**변경 전**: 모든 비-파일 경로에 `/index.html` 추가
**변경 후**: 정적 라우트는 해당 디렉토리의 `index.html`, 동적 라우트는 루트 `/index.html`로 폴백

```javascript
// 업데이트된 로직
var staticRoutes = ['/', '/auth/login', '/lawyer', '/lawyer/cases', ...];

if (isStaticRoute) {
    request.uri = uri + 'index.html';
} else {
    // 동적 라우트: 루트 index.html로 폴백 (클라이언트 라우팅)
    request.uri = '/index.html';
}
```

### 테스트 결과

| 테스트 케이스 | 기대 결과 | 실제 결과 |
|--------------|----------|----------|
| API 인증 실패 | HTTP 401 + JSON | ✅ HTTP 401 + JSON |
| API 권한 없음 | HTTP 403 + JSON | ✅ HTTP 403 + JSON |
| 정적 라우트 `/lawyer/cases` | HTTP 200 + HTML | ✅ HTTP 200 + HTML |
| 동적 라우트 `/lawyer/cases/case_123` | HTTP 200 + HTML | ✅ HTTP 200 + HTML |
| /api/health | HTTP 200 + JSON | ✅ HTTP 200 + JSON |

### 생성된 파일

- `specs/015-fix-async-draft-503/cloudfront-update.json` - CloudFront 설정 파일
- `specs/015-fix-async-draft-503/leh-url-rewrite-updated.js` - CloudFront Function 코드

### 결론

503 에러의 근본 원인은 CloudFront가 API의 403/404 에러를 HTML 페이지로 대체하는 것이었습니다. CustomErrorResponses 제거와 CloudFront Function 수정으로 문제가 해결되었습니다.
