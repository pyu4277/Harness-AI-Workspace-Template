# D3. 요구사항 정의서

## 하네스 엔지니어링 적용
| 기둥 | 역할 |
|------|------|
| 기둥1 | FR/NFR ID를 CLAUDE.md가 인용 가능 |
| 기둥2 | 각 요구사항마다 **검증 방법** 명시 → 훅/테스트가 참조 |
| 기둥3 | 권한 요구사항은 settings.local.json으로 물리 강제 |
| 기둥4 | 위반 시 대응 컬럼이 자기 진화 규칙 생성 기반 |

## Functional Requirements

| ID | 요구사항 | 검증 방법 |
|----|---------|----------|
| FR-001 | 학생 객관 자료(생기부/성적/자격/어학)를 evidence_vault/ 구조화 저장 | evidence_vault/INDEX.md 존재 + 파일 링크 유효 |
| FR-002 | 회차 생성 시 이전 회차 구조+개선 사항 자동 반영 | `/round new` 명령이 기존 구조 복제 + CHANGELOG 항목 추가 |
| FR-003 | 기업 공식 자료(IR/ESG/채용공고)를 기업 프로파일로 자동 수집 | company_profile.md에 3개 이상 원천 링크 |
| FR-004 | 최신 합격 수기/시사/국제정서 리서치 후 회차별 캐시 | research_cache/YYMMDD_queries.md + summary.md |
| FR-005 | 자소서/이력서/포트폴리오 3종 초안을 기업 맞춤으로 생성 | round_N/output/ 3개 파일 생성 완료 |
| FR-006 | 모든 정량/정성 주장은 evidence 링크 또는 인용 출처 필수 | post_tool_validate 훅 통과 |
| FR-007 | 회차 완료 시 CHANGELOG.md에 개선점 + 구조변경 기록 | round_N/CHANGELOG.md 존재 + 형식 검증 |
| FR-008 | 기발한 아이디어 슬롯: 합격 패턴 × 사용자 자료 교차점 3개 이상 제안 | round_N/ideas.md 3개 이상 항목 |
| FR-009 | 기업/양식이 매 회차 변경 가능 (input/ 구조) | round_N/input/company_form.md + job_description.md 필수 |
| FR-010 | 이전 회차 파일 수정 금지 (불변성) | pre_tool_guard 훅이 round_M (M < 현재) 쓰기 차단 |

## Non-Functional Requirements

| ID | 요구사항 | 위반 시 대응 |
|----|---------|-------------|
| NFR-001 | 허위사실 0건 | evidence 없는 수치/주장 발견 → 훅 차단 + 사용자 알림 |
| NFR-002 | 회차당 작업 시 컨텍스트 사용 40% 이하 유지 | research_cache/가 원문 저장 금지, 요약만 |
| NFR-003 | PII(생활기록부 원문 등) 외부 MCP 전송 금지 | pre_tool_guard가 WebSearch/Exa/firecrawl 호출 시 evidence_vault/ 내용 포함 여부 스캔 |
| NFR-004 | 한국어 응답 | CLAUDE.md 규칙 + 훅 검증 |
| NFR-005 | 파일명 `YYMMDD_[이름]_[태그]` 준수 | PostToolUse 훅 파일명 형식 검증 |
| NFR-006 | 코드 작성 ≠ 코드 리뷰 (다른 에이전트) | 상세설계서(D7)에 에이전트 분리 명시 |
| NFR-007 | 리서치 인용 출처 의무 | 인용 없는 외부 주장 → 훅 차단 |
| NFR-008 | 회차별 완결성 (input/ evidence/ research/ output/ 4폴더 필수) | round_N 생성 시 4폴더 누락이면 에러 |

## 회차 운영 요구사항 (프로젝트 고유)

| ID | 요구사항 | 검증 방법 |
|----|---------|----------|
| RR-001 | 회차 번호는 단조 증가 (1차, 2차, 3차 … 삭제/재사용 금지) | `/round new` 스크립트가 max(round_*) + 1 자동 계산 |
| RR-002 | 구조 개선 반영 시 common/ 템플릿 업데이트 | 차기 회차 생성 시 common/ 최신본 복제 |
| RR-003 | 회차 간 독립성: 기업 프로파일은 회차별 분리 | round_N/company_profile.md 존재, 공유 금지 |
| RR-004 | 개선이력은 2차 회차부터 의무 | round_N (N>=2)에 CHANGELOG.md 필수 |
