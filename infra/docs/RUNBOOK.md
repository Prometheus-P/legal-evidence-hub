# RUNBOOK.md — 운영 및 장애 대응 매뉴얼

**버전:** v1.0
**작성일:** 2025-11-19
**대상:** DevOps, On-call 개발자

---

## 🚨 1. 긴급 연락망 및 에스컬레이션 (Escalation Path)

장애 발생 시 상황의 심각도에 따라 아래 순서대로 전파하고 대응합니다.

| 레벨 | 담당자 | 응답 목표 | 호출 기준 |
|:---:|:---:|:---:|:---|
| **Lv 1** | 당직 개발자 (On-call) | 30분 내 | 서비스 접속 불가, 주요 기능 오류 발생 시 |
| **Lv 2** | Tech Lead | 1시간 내 | Lv 1에서 해결 불가하거나 데이터 무결성 이슈 발생 시 |
| **Lv 3** | CTO / PM | 즉시 | 데이터 유출, 보안 사고, 대규모 데이터 손실 등 치명적 장애 시 |

---

## 🛠 2. 장애 유형별 대응 시나리오 (SOP)

### 시나리오 A: AI Worker 멈춤 (업로드 후 무한 '처리 중')
* **증상:** S3에 파일은 정상적으로 업로드되었으나, DynamoDB/OpenSearch에 데이터가 생성되지 않고 UI에서 '처리 중' 상태가 지속됨.
* **진단:**
  ```bash
  # 1. CloudWatch Logs에서 최근 에러 확인
  aws logs filter-log-events --log-group-name /aws/lambda/leh-ai-worker --filter-pattern "ERROR"
  
  # 2. DLQ (Dead Letter Queue)에 쌓인 메시지 확인
  aws sqs get-queue-attributes --queue-url <DLQ_URL> --attribute-names ApproximateNumberOfMessages
  ```

  * **복구 절차:**
    1.  **외부 장애 확인:** OpenAI API Status 페이지를 확인하여 외부 장애인지 파악합니다. (외부 장애 시 공지 후 대기)
    2.  **일시적 오류:** 일시적인 네트워크/API 오류라면 DLQ의 메시지를 원본 큐로 재전송(Redrive)하여 재처리합니다. (AWS Console 또는 스크립트 사용)
    3.  **코드 버그:** 코드 문제로 판명되면 핫픽스 배포 후 `POST /admin/reprocess-evidence {evidence_id}` API를 호출하여 개별 건을 재처리합니다.

### 시나리오 B: 실수로 사건 '종료(삭제)'

  * **상황:** 변호사가 진행 중인 사건을 실수로 '삭제' 버튼을 눌러 종료시킴.
  * **복구 절차 (Soft Delete 복구):**
    1.  **DB 복구:** `cases` 테이블에서 해당 사건의 상태를 `closed`에서 `active`로 변경합니다.
        ```sql
        UPDATE cases SET status = 'active' WHERE id = '{case_id}';
        ```
    2.  **인덱스 복구:** OpenSearch 인덱스가 삭제되었다면, `POST /admin/reindex-case {case_id}` API를 호출하여 DynamoDB에 저장된 데이터를 기반으로 검색 인덱스를 재생성합니다.

### 시나리오 C: OpenAI 비용 급증 (Bill Shock)

  * **상황:** 특정 사건이나 계정에서 비정상적으로 많은 토큰 소모가 감지됨.
  * **대응 절차:**
    1.  **Circuit Breaker 발동:** 해당 `case_id`에 대한 AI 처리를 즉시 일시 정지합니다.
    2.  **로그 분석:** 업로드 로그를 분석하여 악의적인 대량 파일 업로드 공격(DDoS) 여부를 확인합니다.
    3.  **조치:** 공격으로 판단되면 해당 사용자 계정을 블락(Block)하고, 환불 또는 과금 조정을 검토합니다.

-----

## 🧹 3. 정기 점검 리스트 (Weekly)

안정적인 서비스 운영을 위해 매주 다음 항목을 점검합니다.

  - [ ] **S3 버킷 용량:** 불필요한 임시 파일(`tmp/`)이 자동 삭제 규칙(Lifecycle Rule)에 의해 잘 정리되고 있는지 확인합니다.
  - [ ] **RDS 백업:** 최근 자동 스냅샷이 정상적으로 생성되었는지 확인합니다.
  - [ ] **SSL 인증서:** 도메인 SSL 인증서의 만료일을 확인하고 자동 갱신 여부를 체크합니다.
  - [ ] **Audit Log 샘플링:** 감사 로그에 민감 정보(주민번호, 비밀번호 등)가 평문으로 남지 않았는지 무작위로 샘플링하여 검사합니다.

---

## 🌐 4. CloudFront + S3 정적 호스팅 404 대응 (SPA Fallback)

Next.js를 `next export`로 배포하는 현재 구성에서는 `/staff/progress` 같이 사전에 생성되지 않은 경로로 진입 시 404가 발생합니다. 이를 근본적으로 줄이기 위해 S3/CloudFront를 SPA fallback 모드로 설정합니다.

1. **S3 Website Hosting 설정**
   - AWS Console → S3 → 정적 사이트를 호스팅하는 버킷 선택.
   - `Properties → Static website hosting` 활성화.
   - **Index document** = `index.html`, **Error document** = `index.html` 로 동일하게 설정.
   - (CLI)  
     ```bash
     aws s3 website s3://<bucket-name>/ --index-document index.html --error-document index.html
     ```

2. **CloudFront 에러 응답 커스터마이징**
   - CloudFront 배포 → `Error pages`.
   - `Create custom error response` 에서 **404**와 **403** 두 가지를 추가:
     - HTTP Error Code: 403/404
     - TTL: 0 (즉시 반영)
     - Customize Error Response = Yes
     - Response Page Path = `/index.html`
     - HTTP Response Code = 200
   - 배포를 저장 후 `Invalidations → Create invalidation` 으로 `/*` 무효화.

3. **검증**
   - `curl -I https://<cf-domain>/staff/progress` → 200 확인.
   - 브라우저에서 직접 `/staff/progress`, `/staff/<임의경로>` 새로고침 시 SPA가 정상으로 렌더되는지 체크.
   - CloudFront 로그에서 404 비율이 감소했는지 Athena/CloudWatch Logs Insight로 모니터링.

> 위 설정으로 모든 경로가 `index.html`을 반환하므로, 추가적인 auth 가드는 클라이언트/서버 모두에서 유지해야 합니다.

---

## 🚀 5. SSR(서버 사이드 렌더링) 호스팅 전환 로드맵

실시간 데이터를 많이 사용하는 `/staff/progress` 페이지는 장기적으로 SSR 또는 하이브리드 모드가 안정적입니다. 아래 단계에 따라 점진적으로 전환합니다.

1. **인프라 선택**
   - **권장**: AWS Amplify Hosting 또는 Vercel (Next.js 호환).
   - 대안: CloudFront + Lambda@Edge + S3 (Next.js `serverless` 타깃) 또는 ECS/Fargate에서 `next start`.

2. **환경 변수 / 시크릿 정리**
   - `NEXT_PUBLIC_API_BASE_URL`, `AUTH_SECRET` 등을 AWS Parameter Store 또는 Secrets Manager로 옮기고, Amplify/Vercel 환경 변수로 주입.

3. **CI/CD 변경**
   - GitHub Actions에서 `npm install && npm run build` 후 SSR 플랫폼에 배포하도록 워크플로우 추가.
   - 기존 정적 아티팩트 업로드 스텝 제거.

4. **라우팅/보안 점검**
   - `middleware.ts` 또는 Route Handlers로 서버 측 권한 체크 추가.
   - `getServerSideProps` / `app router`의 `fetch` 요청이 백엔드 VPC 엔드포인트를 바라보도록 환경 구성.

5. **롤아웃 계획**
   - Stage 배포 → QA → CloudFront DNS 스위치(또는 Route53 가중치 전환).
   - 롤백: 기존 정적 배포 버킷/배포를 유지하고, 문제가 생기면 DNS를 원래대로 복구.

6. **모니터링**
   - Amplify/Vercel 빌드 로그, Lambda@Edge 로그, CloudWatch Alarms 등을 구성.
   - SSR 전환 후 TTFB가 SLA 내인지 Synthetic Monitoring (Pingdom, CloudWatch Synthetics)으로 측정.

위 로드맵을 실행하면, 실시간 데이터가 필요한 페이지도 404 없이 안전하게 제공되고, 서버 측 렌더링으로 초기 로딩과 SEO, 권한 제어가 강화됩니다.
