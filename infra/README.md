# Infra

이 디렉터리에는 Terraform, CloudFront Functions, 배포 스크립트 등 인프라/배포 관련 리소스를 저장합니다.

## 현재 구조

```
infra/
├── cloudfront-functions/     # CloudFront Edge Functions
│   ├── dynamic-route-handler.js
│   └── README.md
├── terraform/                # AWS IaC 모듈 (진행 중)
├── docs/                     # 인프라 다이어그램, 가이드
├── cloudwatch-dashboard.json # CloudWatch 대시보드 설정
└── s3-lifecycle-policy.json  # S3 버킷 수명 주기 정책
```

## 주요 구성 요소

### CloudFront Functions
- `dynamic-route-handler.js` - Next.js 정적 내보내기의 동적 라우팅 처리
- 자세한 배포 방법은 `cloudfront-functions/README.md` 참조

### Terraform
- AWS 인프라 IaC 모듈 (구성 중)

### 운영 설정
- `cloudwatch-dashboard.json` - 모니터링 대시보드 JSON 템플릿
- `s3-lifecycle-policy.json` - S3 객체 수명 주기 정책
