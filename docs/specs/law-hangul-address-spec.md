
# 국가법령정보센터 법령한글주소(Law Hangul Address) 기술 명세서

- **문서 목적**  
  외부 시스템(웹·백엔드·AI 에이전트)이 `법령명/사건명/조약명 + 번호 + 날짜`만으로 **유효한 국가법령정보센터 딥링크(URL)** 를 생성할 수 있도록, 법령 한글주소 규칙을 **기계가 바로 구현 가능한 형식**으로 정리한다.
- **대상 서비스**
  - 국가법령정보센터: `https://www.law.go.kr`
  - 국가법령정보 공동활용 개발자 LAB > 법령 한글주소 안내
- **Base URL**
  - 모든 예시는 `https://www.law.go.kr` 기준 Path 만 기술한다.

---

## 1. 공통 규칙 (Common Rules)

### 1.1 Path 기본 구조

```text
/{RootPrefix}/{Title or Category}/{OptionalSubPath}/{OptionalBracketParams}
```

- **RootPrefix**: 분야 구분(법령, 영문법령, 행정규칙, 자치법규, 학칙공단, 조약, 판례, 헌재결정례, 법령해석례, 행정심판례, 법령체계도, 용어, 각종 위원회 등)
- **Title**: 법령명, 판례명, 사건명, 안건명, 조약명 등(한글 그대로)
- **OptionalSubPath**: 조문(제X조), 부칙, 제개정문, 신구법비교, 삼단비교 등
- **OptionalBracketParams**: 괄호 `()` 안에 콤마로 연결된 번호/날짜 (공포번호, 발령번호, 사건번호, 의결일자 등)

### 1.2 인코딩 규칙 (Encoding)

- **문자 인코딩**: UTF-8
- **URL 인코딩 대상**
  - 한글, 공백, 특수문자(쉼표, 괄호, 슬래시 등)는 최종 HTTP 요청 시 **URL 인코딩**해야 한다.
  - Path 설계 시에는 **사람 기준 원문**을 그대로 사용하되, 구현에서는 `encodeURIComponent`/`urlencode` 등으로 처리한다.
- **인코딩 단위 권장**
  - 최소 단위: **Path segment** 또는 괄호 내 전체 문자열
  - 예:  
    - 설계값: `/법령/자동차관리법/제3조`  
    - 실제 요청: `/법령/%EC%9E%90%EB%8F%99%EC%B0%A8%EA%B4%80%EB%A6%AC%EB%B2%95/%EC%A0%9C3%EC%A1%B0`

### 1.3 날짜 및 번호 포맷

- **날짜(`date_val`, `enforce_date`, `의결일자`, `해석일자` 등)**: `YYYYMMDD`
- **각종 번호(`identifier` 등)**: 사이트에 표기된 문자열을 그대로 사용
  - 숫자/한글/영문/하이픈·공백 모두 포함
  - 예: `2013다214529`, `제2018-26-324호`, `비정규직대책팀-3018`

---

## 2. 데이터베이스 스키마 (DB Schema Reference)

### 2.1 공통 메타데이터 엔티티

법령/판례/위원회 결정 등 모든 리소스를 추상화한 공통 엔티티 예시:

| 필드명 (Logical) | 필드명 (Physical) | 타입 | 설명 | 필수 |
| :--------------- | :---------------- | :--- | :--- | :--- |
| 자료구분         | `category_code`   | String | `법령`, `행정규칙`, `판례`, `헌재결정례`, `조세심판재결례` 등 최상위 Prefix | **Y** |
| 세부분류         | `subcategory`     | String | `제개정문`, `신구법비교`, `삼단비교`, `법령체계도/판례` 등 세부 기능 구분 | N |
| 명칭/제목        | `title`           | String | 법령명, 판례명, 사건명, 안건명, 조약명 등 | **Y** |
| 세부식별자       | `identifier`      | String | 공포번호, 발령번호, 사건번호, 안건번호, 조약번호 등 | N |
| 날짜             | `date_val`        | String(8) | 공포일자, 판결일자, 의결일자, 해석일자 등 | N |
| 시행일자         | `enforce_date`    | String(8) | 법령 시행일자(시행기준 링크에 사용) | N |
| 부가정보         | `sub_item`        | String | `제3조`, `부칙`, `부칙(19466,20060508)`, `별표28의2`, `서식79` 등 | N |
| 기관명/위원회명  | `org_name`        | String | 개인정보보호위원회, 공정거래위원회, 조세심판원 등 | N |
| 카테고리 메모    | `meta_note`       | Text | 원본 안내 문구나 예외 규칙 설명 | N |

> **인덱스 권장**
> - `(category_code, title)`
> - `(category_code, identifier)`
> - `(category_code, title, date_val)`

---

## 3. 카테고리 및 Prefix 매핑

### 3.1 최상위 Prefix 목록

| category_code (예시) | Prefix (Path)        | 설명 |
| -------------------- | -------------------- | ---- |
| `STATUTE`            | `/법령`              | 일반 법령 |
| `STATUTE_EN`         | `/영문법령`          | 영문 번역 법령 |
| `ADMIN_RULE`         | `/행정규칙`          | 행정규칙 |
| `LOCAL_LAW`          | `/자치법규`          | 지방자치단체 조례 등 |
| `SCHOOL_CORP`        | `/학칙공단`          | 학칙/공단 관련 규정·협약 |
| `TREATY`             | `/조약`              | 조약 |
| `CASE_SUPREME`       | `/판례`              | 대법원 판례 |
| `CASE_CONST`         | `/헌재결정례`        | 헌법재판소 결정례 |
| `CASE_INTERPRET`     | `/법령해석례`        | 법령해석례 |
| `CASE_ADMIN_APPEAL`  | `/행정심판례`        | 행정심판례 |
| `FORM_STATUTE`       | `/법령별표서식`      | 법령 별표·서식 |
| `FORM_ADMIN_RULE`    | `/행정규칙별표서식`  | 행정규칙 별표·서식 |
| `FORM_LOCAL`         | `/자치법규별표서식`  | 자치법규 별표·서식 |
| `SYSTEM_MAP`         | `/법령체계도`        | 법령/판례/해석례/심판례 체계도 |
| `TERM`               | `/용어`              | 법령 용어 사전 |
| `COMMITTEE_*`        | `/개인정보보호위원회` 등 | 각종 위원회·위원회 재결 |
| `CENTRAL_INTERP`     | `/중앙부처1차해석`    | 중앙부처 1차 법령해석 |
| `TAX_TRIBUNAL`       | `/조세심판재결례`    | 조세심판재결례 |
| `IP_TRIBUNAL`        | `/특허심판재결례`    | 특허심판재결례 |
| `MARINE_SAFETY_TR`   | `/해양안전심판재결례`| 해양안전심판재결례 |
| `ACRC_TR`            | `/국민권익위원회심판재결례` | 국민권익위 심판재결례 |
| `MPSS_TR`            | `/인사혁신처소청심사위원회심판재결례` | 인사혁신처 소청심사위 재결 |

**실제 DB 설계 시** `category_code`는 위 예시처럼 영문 코드로, 화면·API 레벨에서는 한글 Prefix를 사용하면 된다.

---

## 4. 법령 (Statutes) & 영문법령

### 4.1 법령 `/법령`

#### 4.1.1 기본 조회

| 유형        | 패턴                          | 매핑 |
| ----------- | ----------------------------- | ---- |
| 기본        | `/법령/{title}`               | `title` = 법령명 또는 약칭 |
| 조문        | `/법령/{title}/{sub_item}`    | `sub_item` = `제X조`, `제45조의3` 등 |
| 부칙(개요)  | `/법령/{title}/부칙`          | 부칙 목록 |
| 부칙(상세)  | `/법령/{title}/부칙({identifier},{date_val})` | `identifier` = 부칙번호, `date_val` = 부칙일자 |
| 삼단비교(1) | `/법령/{title}/삼단비교`      | 해당 법령 삼단비교 |
| 삼단비교(2) | `/법령/3단비교/{title}`       | 동일 기능, 다른 Prefix 방식 |

#### 4.1.2 연혁·시행일 기준

| 유형           | 패턴                                        | 매핑 |
| -------------- | ------------------------------------------- | ---- |
| 연혁(공포번호) | `/법령/{title}/({identifier})`              | `identifier` = 공포번호 |
| 연혁(상세)     | `/법령/{title}/({identifier},{date_val})`   | `identifier` = 공포번호, `date_val` = 공포일자 |
| 시행일 기준    | `/법령/{title}/({enforce_date},{identifier},{date_val})` | `enforce_date` = 시행일, 나머지 동일 |

#### 4.1.3 제개정문·신구법비교

| 유형                 | 패턴                                                  | 설명 |
| -------------------- | ----------------------------------------------------- | ---- |
| 제개정문 기본        | `/법령/제개정문/{title}`                             | 최신 제개정문 |
| 제개정문(공포일자)   | `/법령/제개정문/{title}/({identifier},{date_val})`   | 특정 공포번호·공포일 기준 |
| 제개정문(시행일자)   | `/법령/제개정문/{title}/({enforce_date},{identifier},{date_val})` | 시행일 기준 상세 |
| 신구법비교 기본      | `/법령/신구법비교/{title}`                           | 신·구조문 대비표 |
| 신구법비교(공포일자) | `/법령/신구법비교/{title}/({identifier},{date_val})` |
| 신구법비교(시행일자) | `/법령/신구법비교/{title}/({enforce_date},{identifier},{date_val})` |

#### 4.1.4 최신 정보

| Path              | 설명         |
| ----------------- | ------------ |
| `/법령/최신공포법령` | 최신 공포 법령 목록 |
| `/법령/최신시행법령` | 최신 시행 법령 목록 |
| `/법령/시행예정법령` | 시행 예정 법령 목록 |

### 4.2 영문법령 `/영문법령`

영문 번역 법령에 대한 주소 규칙.

| 유형        | 패턴                                      | 매핑 |
| ----------- | ----------------------------------------- | ---- |
| 기본        | `/영문법령/{title}`                       | `title` = 법령명(한글 기준) |
| 특정 버전   | `/영문법령/{title}/({identifier},{date_val})` | `identifier` = 공포번호, `date_val` = 공포일자 |

---

## 5. 행정규칙·자치법규·학칙공단·조약

### 5.1 행정규칙 `/행정규칙`

| 유형        | 패턴                                      | 매핑 |
| ----------- | ----------------------------------------- | ---- |
| 기본        | `/행정규칙/{title}`                       | `title` = 행정규칙명 |
| 특정 버전   | `/행정규칙/{title}/({identifier},{date_val})` | `identifier` = 발령번호, `date_val` = 발령일자 |

### 5.2 자치법규 `/자치법규`

| 유형        | 패턴                                      | 매핑 |
| ----------- | ----------------------------------------- | ---- |
| 기본        | `/자치법규/{title}`                       | `title` = 자치법규명 |
| 특정 버전   | `/자치법규/{title}/({identifier},{date_val})` | `identifier` = 공포번호, `date_val` = 공포일자 |

### 5.3 학칙공단 `/학칙공단`

| 유형        | 패턴                                      | 매핑 |
| ----------- | ----------------------------------------- | ---- |
| 기본        | `/학칙공단/{title}`                       | `title` = 학칙/협약명 |
| 특정 버전   | `/학칙공단/{title}/({identifier},{date_val})` | `identifier` = 발령번호, `date_val` = 발령일자 |

### 5.4 조약 `/조약`

| 유형                    | 패턴                                      | 매핑 |
| ----------------------- | ----------------------------------------- | ---- |
| 기본                    | `/조약/{title}`                           | `title` = 조약명 |
| 번호+발효일(단독)       | `/조약/({identifier},{date_val})`        | 제목 없이 번호·발효일만으로 조회 가능 |
| 제목+번호+발효일(일부) | `/조약/{title}/({identifier},{date_val})` | 서비스 동작은 위와 동일 범주 |

- `identifier` = 조약번호
- `date_val` = 발효일자

---

## 6. 판례 및 결정례 (Judicial Precedents)

### 6.1 대법원 판례 `/판례`

| 유형                   | 패턴                                      | 매핑 |
| ---------------------- | ----------------------------------------- | ---- |
| 제목 기반              | `/판례/{title}`                           | `title` = 판례명 |
| 제목+사건번호+판결일   | `/판례/{title}/({identifier},{date_val})` |
| 사건번호 기반(단독)    | `/판례/({identifier})`                    | 사건번호만으로 직접 연결 |
| 사건번호+판결일(단독) | `/판례/({identifier},{date_val})`         |

- `identifier` = 사건번호  
- `date_val` = 판결일자

### 6.2 헌재결정례 `/헌재결정례`

| 유형                    | 패턴                                      | 매핑 |
| ----------------------- | ----------------------------------------- | ---- |
| 제목 기반               | `/헌재결정례/{title}`                     | `title` = 사건명 |
| 제목+사건번호+선고일    | `/헌재결정례/{title}/({identifier},{date_val})` |
| 사건번호 기반(단독·옵션)| `/헌재결정례/({identifier})`, `/헌재결정례/({identifier},{date_val})` |

### 6.3 법령해석례 `/법령해석례`

| 유형                         | 패턴                                      | 매핑 |
| ---------------------------- | ----------------------------------------- | ---- |
| 제목 기반                    | `/법령해석례/{title}`                     |
| 사건번호+해석일자(단독)      | `/법령해석례/({identifier},{date_val})`   |
| 사건번호만(단독)             | `/법령해석례/({identifier})`             |

### 6.4 행정심판례 `/행정심판례`

| 유형                         | 패턴                                      | 매핑 |
| ---------------------------- | ----------------------------------------- | ---- |
| 제목 기반                    | `/행정심판례/{title}`                     |
| 제목+사건번호+의결일자       | `/행정심판례/{title}/({identifier},{date_val})` |

---

## 7. 별표 및 서식 (Forms & Attachments)

### 7.1 법령 별표·서식 `/법령별표서식`

| 유형          | 패턴                                          | 매핑 |
| ------------- | --------------------------------------------- | ---- |
| 기본          | `/법령별표서식/({title},{identifier})`        | `identifier` = `별표X` 또는 `서식X` |
| 시행일 포함* | `/법령별표서식/({title},{enforce_date},{identifier})` | 구현 시 선택적 지원 (공식 안내는 2항목형 위주) |

### 7.2 행정규칙 별표·서식 `/행정규칙별표서식`

| 유형 | 패턴                                          | 매핑 |
| ---- | --------------------------------------------- | ---- |
| 기본 | `/행정규칙별표서식/({title},{sub_id},{identifier})` | `sub_id` = 발령번호(=발행번호), `identifier` = `별표X` |

### 7.3 자치법규 별표·서식 `/자치법규별표서식`

| 유형 | 패턴                                          | 매핑 |
| ---- | --------------------------------------------- | ---- |
| 기본 | `/자치법규별표서식/({title},{sub_id},{identifier})` | `sub_id` = 공포번호, `identifier` = `별표X` or `서식X` |

---

## 8. 법령체계도 (Legal System Map) `/법령체계도`

기본 구조:

```text
/법령체계도/{category}/{title}
또는
/법령체계도/{category}/{title}/({identifier},{date_val})
```

| category (Path) | 설명        | 예시 패턴 |
| --------------- | ----------- | --------- |
| `법령`          | 법령 체계도 | `/법령체계도/법령/{title}` |
| `행정규칙`      | 행정규칙    | `/법령체계도/행정규칙/{title}` |
| `판례`          | 판례        | `/법령체계도/판례/{title}`<br>`/법령체계도/판례/{title}/({identifier},{date_val})` |
| `법령해석례`    | 해석례      | `/법령체계도/법령해석례/{title}`<br>`/법령체계도/법령해석례/{title}/({identifier},{date_val})` |
| `행정심판례`    | 행정심판례  | `/법령체계도/행정심판례/{title}`<br>`/법령체계도/행정심판례/{title}/({identifier},{date_val})` |
| `헌재결정례`    | 헌재결정례  | `/법령체계도/헌재결정례/{title}`<br>`/법령체계도/헌재결정례/{title}/({identifier},{date_val})` |

---

## 9. 위원회별 상세 라우팅 (Committee Decisions)

공통 규칙:

```text
/{위원회명}/{title}/({identifier[,date_val]})
```

- `title` = 사건명 또는 안건명
- `identifier` = 사건번호/의결번호/재결번호 등
- `date_val` = 의결일자(있는 경우)

### 9.1 대표 위원회 패턴

| Prefix                        | identifier 의미 | 기본 패턴 예 |
| ----------------------------- | -------------- | ------------ |
| `/개인정보보호위원회`         | 사건번호        | `/개인정보보호위원회/{title}/({identifier})` |
| `/고용보험심사위원회`         | 사건번호        | `/고용보험심사위원회/{title}/({identifier})` |
| `/공정거래위원회`             | 사건번호        | `/공정거래위원회/{title}/({identifier})` |
| `/국민권익위원회`             | 사건번호        | `/국민권익위원회/{title}/({identifier})` |
| `/금융위원회`                 | 의결번호        | `/금융위원회/{title}/({identifier})` |
| `/방송미디어통신위원회`       | 안건번호        | `/방송미디어통신위원회/{title}/({identifier})` |
| `/산업재해보상보험재심사위원회`| 사건번호        | `/산업재해보상보험재심사위원회/{title or '사건'}/{identifier}` |
| `/노동위원회`                 | 사건번호        | `/노동위원회/{title}/({identifier})` |
| `/중앙토지수용위원회`         | 제목만          | `/중앙토지수용위원회/{title}` |
| `/중앙환경분쟁조정위원회`     | 의결번호        | `/중앙환경분쟁조정위원회/{title}/({identifier})` |
| `/국가인권위원회`             | 사건번호(+의결일)| `/국가인권위원회/{title}/({identifier})`, `/.../({identifier},{date_val})` |

> **실무 팁**  
> DB에서는 모든 위원회를 `COMMITTEE_DECISION` 같은 상위 카테고리로 묶고, `org_name`에 위원회명, `identifier`·`date_val` 조합으로 정규화하는 것이 Query·URL 생성 양쪽에서 편하다.

---

## 10. 중앙부처 1차 법령해석 `/중앙부처1차해석`

여러 중앙부처가 **단일 Endpoint**를 공유하며, 부처명은 URL Path에 노출되지 않는다.

- **Base**: `/중앙부처1차해석`
- **title**: 안건명
- **identifier**: 안건번호
- **date_val**: 해석일자

| 유형                    | 패턴                                      | 설명 |
| ----------------------- | ----------------------------------------- | ---- |
| 제목만                  | `/중앙부처1차해석/{title}`               | 안건명만으로 조회 |
| 제목+안건번호           | `/중앙부처1차해석/{title}/({identifier})` |
| 제목+안건번호+해석일자  | `/중앙부처1차해석/{title}/({identifier},{date_val})` |

DB 설계 시 예시:

- `category_code` = `CENTRAL_INTERP`
- `org_name` = `고용노동부`, `국토교통부`, `기상청` 등
- `title`, `identifier`, `date_val` 필수 수준으로 관리

---

## 11. 기타 재결례 (Other Tribunals)

### 11.1 조세심판재결례 `/조세심판재결례`

| 유형                        | 패턴                                             |
| --------------------------- | ------------------------------------------------ |
| 제목만                      | `/조세심판재결례/{title}`                        |
| 제목+청구번호               | `/조세심판재결례/{title}/({청구번호})`          |
| 제목+청구번호+의결일자      | `/조세심판재결례/{title}/({청구번호},{date_val})` |

### 11.2 특허심판재결례 `/특허심판재결례`

| 유형           | 패턴                                             |
| -------------- | ------------------------------------------------ |
| 제목+청구번호  | `/특허심판재결례/{title}/({청구번호})`          |

### 11.3 해양안전심판재결례 `/해양안전심판재결례`

| 유형                          | 패턴                                                   |
| ----------------------------- | ------------------------------------------------------ |
| 제목+재결번호                 | `/해양안전심판재결례/{title}/({재결번호})`           |
| 제목+재결번호+의결일자(옵션)  | `/해양안전심판재결례/{title}/({재결번호},{date_val})` |

### 11.4 국민권익위원회심판재결례 `/국민권익위원회심판재결례`

| 유형                            | 패턴                                                             |
| ------------------------------- | ---------------------------------------------------------------- |
| 제목+사건번호                   | `/국민권익위원회심판재결례/{title}/({사건번호})`                |
| 제목+사건번호+의결일자          | `/국민권익위원회심판재결례/{title}/({사건번호},{date_val})`     |

### 11.5 인사혁신처소청심사위원회심판재결례 `/인사혁신처소청심사위원회심판재결례`

| 유형           | 패턴                                                             |
| -------------- | ---------------------------------------------------------------- |
| 제목+사건번호  | `/인사혁신처소청심사위원회심판재결례/{title}/({사건번호})`      |

---

## 12. 용어 사전 `/용어`

- **Prefix**: `/용어`
- **패턴**: `/용어/{term}`
- **예시**: `/용어/선박`

DB 예시:

- `category_code` = `TERM`
- `title` = 용어 (`선박`)
- 추가 설명은 별도 사전 테이블과 연계 가능

---

## 13. URL 생성 알고리즘 (Implementation Guide)

### 13.1 카테고리별 패턴 선택 로직 개요

1. **category_code → Prefix 매핑**
   - `STATUTE` → `/법령`
   - `STATUTE_EN` → `/영문법령`
   - `ADMIN_RULE` → `/행정규칙`
   - `LOCAL_LAW` → `/자치법규`
   - `SCHOOL_CORP` → `/학칙공단`
   - `TREATY` → `/조약`
   - `CASE_SUPREME` → `/판례`
   - `CASE_CONST` → `/헌재결정례`
   - `CASE_INTERPRET` → `/법령해석례`
   - `CASE_ADMIN_APPEAL` → `/행정심판례`
   - `FORM_STATUTE` → `/법령별표서식`
   - `FORM_ADMIN_RULE` → `/행정규칙별표서식`
   - `FORM_LOCAL` → `/자치법규별표서식`
   - `SYSTEM_MAP` → `/법령체계도`
   - `TERM` → `/용어`
   - `CENTRAL_INTERP` → `/중앙부처1차해석`
   - `TAX_TRIBUNAL` → `/조세심판재결례`
   - `IP_TRIBUNAL` → `/특허심판재결례`
   - `MARINE_SAFETY_TR` → `/해양안전심판재결례`
   - `ACRC_TR` → `/국민권익위원회심판재결례`
   - `MPSS_TR` → `/인사혁신처소청심사위원회심판재결례`
   - `COMMITTEE_*` → `/개인정보보호위원회` 등 `org_name` 그대로 사용

2. **세부 유형 결정**
   - `subcategory` or 호출 컨텍스트에 따라 패턴 결정:
     - `ARTICLE` → 조문(`/법령/{title}/{sub_item}`)
     - `SUPPLEMENT` → 부칙(`/법령/{title}/부칙(...)`)
     - `AMENDMENT_DOC` → 제개정문(`/법령/제개정문/...`)
     - `OLD_NEW_COMPARE` → 신구법비교(`/법령/신구법비교/...`)
     - `SYSTEM_MAP` → `/법령체계도/{category}/{title}`

3. **괄호 파라미터 정렬 규칙**
   - **법령**: `(enforce_date?, identifier?, date_val?)`
   - **행정규칙/자치법규**: `(identifier, date_val)`
   - **판례·재결례**: `(identifier, date_val?)`
   - **조세·특허·해양·심판재결례**: 각 카테고리별 정의대로 배치(11장 표)

4. **문자열 조합**
   - 괄호 내부는 **콤마 기준**으로 그대로 Join
   - 전체를 한 번에 URL 인코딩하거나, 각 segment 별 인코딩

### 13.2 Python 스타일 수도코드

```python
from urllib.parse import quote

BASE_URL = "https://www.law.go.kr"

PREFIX_MAP = {
    "STATUTE": "/법령",
    "STATUTE_EN": "/영문법령",
    "ADMIN_RULE": "/행정규칙",
    "LOCAL_LAW": "/자치법규",
    "SCHOOL_CORP": "/학칙공단",
    "TREATY": "/조약",
    "CASE_SUPREME": "/판례",
    "CASE_CONST": "/헌재결정례",
    "CASE_INTERPRET": "/법령해석례",
    "CASE_ADMIN_APPEAL": "/행정심판례",
    "FORM_STATUTE": "/법령별표서식",
    "FORM_ADMIN_RULE": "/행정규칙별표서식",
    "FORM_LOCAL": "/자치법규별표서식",
    "SYSTEM_MAP": "/법령체계도",
    "TERM": "/용어",
    "CENTRAL_INTERP": "/중앙부처1차해석",
    "TAX_TRIBUNAL": "/조세심판재결례",
    "IP_TRIBUNAL": "/특허심판재결례",
    "MARINE_SAFETY_TR": "/해양안전심판재결례",
    "ACRC_TR": "/국민권익위원회심판재결례",
    "MPSS_TR": "/인사혁신처소청심사위원회심판재결례",
    # 위원회 계열은 org_name을 prefix로 직접 사용
}

def url_seg(s: str) -> str:
    """경로 segment 인코딩"""
    return quote(s, safe="")

def build_bracket(*parts: str) -> str:
    """빈값 제외 후 콤마 연결하여 괄호 문자열 생성"""
    vals = [p for p in parts if p]
    if not vals:
        return ""
    inner = ",".join(vals)
    return f"/({url_seg(inner)})"

def generate_law_url(
    category_code: str,
    title: str | None = None,
    identifier: str | None = None,
    date_val: str | None = None,
    enforce_date: str | None = None,
    sub_item: str | None = None,
    subcategory: str | None = None,
    org_name: str | None = None,
) -> str:
    """
    국가법령정보 법령한글주소 생성기.
    - category_code & subcategory 조합으로 패턴 결정
    - title/identifier/date_val/enforce_date/sub_item 사용
    """
    # 1) Prefix 결정
    if category_code.startswith("COMMITTEE_"):
        # 위원회 계열: org_name을 그대로 Path 로 사용
        if not org_name:
            raise ValueError("committee category requires org_name")
        prefix = "/" + org_name
    else:
        prefix = PREFIX_MAP.get(category_code)
        if not prefix:
            # 미등록 카테고리는 category_code를 그대로 사용
            prefix = "/" + category_code

    path = prefix

    # 2) 서브카테고리(제개정문, 신구법비교, 체계도 등) 반영
    if category_code == "STATUTE" and subcategory in {"AMENDMENT_DOC", "OLD_NEW_COMPARE"}:
        if subcategory == "AMENDMENT_DOC":
            path += "/제개정문"
        elif subcategory == "OLD_NEW_COMPARE":
            path += "/신구법비교"

    if category_code == "SYSTEM_MAP":
        # SYSTEM_MAP 의 경우: subcategory 가 "법령", "판례" 등
        if not subcategory:
            raise ValueError("SYSTEM_MAP requires subcategory like '법령', '판례'")
        path += f"/{url_seg(subcategory)}"

    # 3) Title / Term / Case name
    # (용어, 조세심판재결례 등 일부 카테고리는 title 가 필수)
    if title and category_code not in {"FORM_STATUTE", "FORM_ADMIN_RULE", "FORM_LOCAL"}:
        path += f"/{url_seg(title)}"

    # 4) sub_item(조문/부칙/별표/서식) 처리
    if category_code == "STATUTE" and sub_item:
        # 예: 제3조, 부칙, 부칙(19466,20060508), 삼단비교 등
        path += f"/{url_seg(sub_item)}"

    # 5) 괄호 파라미터 조합 (카테고리별 규칙 예시)
    bracket = ""

    if category_code == "STATUTE":
        # 법령: (enforce_date?, identifier?, date_val?)
        bracket = build_bracket(enforce_date, identifier, date_val)

    elif category_code in {"ADMIN_RULE", "LOCAL_LAW", "SCHOOL_CORP", "TREATY"}:
        # (identifier, date_val) 조합
        bracket = build_bracket(identifier, date_val)

    elif category_code in {
        "CASE_SUPREME",
        "CASE_CONST",
        "CASE_INTERPRET",
        "CASE_ADMIN_APPEAL",
        "TAX_TRIBUNAL",
        "IP_TRIBUNAL",
        "MARINE_SAFETY_TR",
        "ACRC_TR",
        "MPSS_TR",
    }:
        # (identifier, date_val?) – 일부는 날짜 생략 가능
        bracket = build_bracket(identifier, date_val)

    elif category_code == "CENTRAL_INTERP":
        # 중앙부처1차해석: (identifier, date_val?)
        bracket = build_bracket(identifier, date_val)

    elif category_code in {"FORM_STATUTE", "FORM_ADMIN_RULE", "FORM_LOCAL"}:
        # 별표/서식: 모든 파라미터를 title, identifier, sub_id 등 외부에서 미리 조합해서 넘기도록 설계해도 된다.
        # 여기서는 identifier 에 "법령명,별표X" 등 전체를 전달한다고 가정할 수도 있음.
        if identifier and not title:
            bracket = build_bracket(identifier)

    # 괄호 문자열 부착
    path += bracket

    return BASE_URL + path
```

---

## 14. 부록: 카테고리 코드 설계 예시

```text
STATUTE                     # 법령
STATUTE_EN                  # 영문법령
ADMIN_RULE                  # 행정규칙
LOCAL_LAW                   # 자치법규
SCHOOL_CORP                 # 학칙공단
TREATY                      # 조약
CASE_SUPREME                # 대법원 판례
CASE_CONST                  # 헌재결정례
CASE_INTERPRET              # 법령해석례
CASE_ADMIN_APPEAL           # 행정심판례
FORM_STATUTE                # 법령별표서식
FORM_ADMIN_RULE             # 행정규칙별표서식
FORM_LOCAL                  # 자치법규별표서식
SYSTEM_MAP                  # 법령체계도
TERM                        # 법령 용어 사전
COMMITTEE_PIPC              # 개인정보보호위원회
COMMITTEE_FTC               # 공정거래위원회
COMMITTEE_ACRC              # 국민권익위원회
COMMITTEE_FSC               # 금융위원회
...                         # 기타 위원회들
CENTRAL_INTERP              # 중앙부처 1차 해석
TAX_TRIBUNAL                # 조세심판재결례
IP_TRIBUNAL                 # 특허심판재결례
MARINE_SAFETY_TR            # 해양안전심판재결례
ACRC_TR                     # 국민권익위 심판재결례
MPSS_TR                     # 인사혁신처 소청심사위 재결
```

---

### 참고

본 명세서는 **법제처 국가법령정보 공동활용 개발자 LAB의 ‘법령 한글주소’ 안내 페이지**를 토대로,  
AI 에이전트와 백엔드 개발자가 곧바로 **DB 스키마 설계·URL 생성 로직 구현**에 사용할 수 있도록 구조화한 기술 사양이다.
