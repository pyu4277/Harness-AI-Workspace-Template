# D10. 순서도 및 절차도

회차 전체 실행 흐름과 의사결정 분기를 도식화.

## 하네스 엔지니어링 적용
| 기둥 | 역할 |
|------|------|
| 기둥1 | 흐름 단계가 CLAUDE.md "작업 순서" 섹션의 기준 |
| 기둥2 | 각 단계의 Exit 조건이 훅 검증 |
| 기둥3 | 단계별 허용 도구 변경 |
| 기둥4 | 단계 실패 시 자동 회복 절차 포함 |

## 1. 회차 전체 순서도

```mermaid
flowchart TD
  S([회차 시작]) --> A{evidence_vault<br/>준비됨?}
  A -- No --> A1[UC-01 실행<br/>자료 등록]
  A1 --> A
  A -- Yes --> B[/round new]
  B --> C[input/ 3종 투입<br/>company_form + JD + meta]
  C --> D[researcher 실행<br/>4종 리서치]
  D --> E{리서치<br/>성공?}
  E -- No --> E1[캐시 대체 + 사용자 알림]
  E -- Yes --> F[company_profile.md<br/>작성]
  E1 --> F
  F --> G[ideator 실행<br/>ideas.md 3+]
  G --> H[사용자 아이디어 선택]
  H --> I[writer 실행<br/>output 3종 작성]
  I --> J[/clear<br/>새 세션]
  J --> K[reviewer 실행<br/>독립 검증]
  K --> L{CRITICAL/HIGH<br/>있음?}
  L -- Yes --> M[writer 세션<br/>복귀 후 수정]
  M --> K
  L -- No --> N[사용자 최종 검토]
  N --> O{승인?}
  O -- No --> M
  O -- Yes --> P{N>=2?}
  P -- Yes --> Q[CHANGELOG.md<br/>작성]
  P -- No --> R[회차 종료]
  Q --> R
  R --> S2([End])
```

## 2. 리서치 절차도 (researcher 에이전트)

```mermaid
flowchart LR
  R1[기업명/직무/산업 수신] --> R2[쿼리 템플릿 생성]
  R2 --> R3[WebSearch<br/>합격 수기]
  R2 --> R4[Exa 심층<br/>합격 자소서 공유]
  R2 --> R5[firecrawl<br/>IR/공시]
  R2 --> R6[WebSearch+WebFetch<br/>경제/사회/국제]
  R3 & R4 --> R7[01_합격수기/]
  R6 --> R8[02_시사맥락/]
  R5 --> R9[03_기업IR/<br/>04_ESG/]
  R7 & R8 & R9 --> R10[summary.md<br/>통합 요약]
```

## 3. 회차 구조 개선 절차

```mermaid
flowchart TD
  X1[회차 수행 중<br/>구조 불편 발견] --> X2[temp_improvements.md<br/>메모]
  X2 --> X3[회차 종료 시<br/>CHANGELOG에 정리]
  X3 --> X4{구조 개선이<br/>common/ 반영?}
  X4 -- Yes --> X5[common/ 업데이트]
  X4 -- No --> X6[round_N 국소 반영]
  X5 --> X7[차기 회차가<br/>common/ 복제 시 자동 상속]
```

## 4. 의사결정 분기 요약

| 분기 | 기준 | 행동 |
|---|---|---|
| evidence_vault 준비 | INDEX.md 존재 | 없으면 UC-01 선행 |
| 리서치 성공 | research_cache/round_N/summary.md 생성 | 실패 시 캐시 대체 |
| reviewer 판정 | CRITICAL/HIGH 0건 | 있으면 writer 복귀 |
| 사용자 승인 | 수동 | 거부 시 writer 복귀 |
| CHANGELOG 필요 | N >= 2 | 필수 작성 |
