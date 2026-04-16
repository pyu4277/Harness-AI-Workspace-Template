# Architecture Decision Record

> 각 결정은 WHY 중심 3줄 요약 + Alternatives + Consequences.

## ADR-001: 하위 프로젝트 구조 대신 회차 폴더 구조 채택
- 일자: 2026-04-14
- 상태: 채택

**Context**: 한 명의 학생이 합격할 때까지 **여러 기업에 반복 지원**한다. 각 지원서는 독립 산출물이지만, 학생의 evidence/합격 패턴/템플릿은 공유.

**Decision**: 하위 프로젝트(`projectA/`, `projectB/`)가 아닌 **회차 폴더**(`round_1/`, `round_2/`, …) 구조 채택. 공용 자산은 `common/`, 학생 자료는 `evidence_vault/`, 리서치는 `research_cache/round_N/`.

**Why**: 하위 프로젝트 구조는 공용 자산 중복 또는 파편화 유발. 회차 구조는 (a) evidence_vault 단일 소스, (b) 회차 간 개선이력 추적 자연스러움, (c) 재지원 처리가 동일 패턴.

**Alternatives**:
- `projects/<기업명>/` — 기각. 동일 기업 재지원 처리 애매.
- 플랫 구조 (날짜 기반) — 기각. 개선이력 추적 불가.

**Consequences**: 회차 단조 증가, 불변성 규칙 필수. 이 둘은 pre_tool_guard 훅이 강제.

---

## ADR-002: 이전 회차 파일 불변성 (회차 수정 금지)
- 일자: 2026-04-14
- 상태: 채택

**Context**: 회차 간 품질 상승을 측정하려면 이전 회차가 보존되어야 한다. 수정 허용 시 품질 변화 측정 의미 상실.

**Decision**: round_M (M < 현재)은 Write/Edit 불가. 개선은 신규 회차에서만.

**Why**: (a) 회차간 품질 비교 무결성, (b) "언제 무엇이 개선되었는지" 감사 가능, (c) 구조 개선과 데이터 변경 분리 (CHANGELOG).

**Alternatives**: 소프트 경고만. 기각. 프롬프트는 부탁이라 실수 재발.

**Consequences**: pre_tool_guard 훅이 경로 기반으로 물리 차단. 실수로 수정 시도해도 차단됨.

---

## ADR-003: evidence_vault 불변성 + 외부 MCP 전송 금지
- 일자: 2026-04-14
- 상태: 채택

**Context**: 학생 개인정보(생활기록부, 성적, 자격증)는 민감 PII. 외부 MCP(WebSearch/Exa/firecrawl)에 전달 시 영구 로그 가능성.

**Decision**: evidence_vault/ Write/Edit 차단. MCP 호출 파라미터에 evidence_vault 경로/내용 포함 시 차단.

**Why**: Shift Left — 에이전트가 실수로 PII를 쿼리에 넣으려 해도 훅이 입력 단계에서 차단. 프롬프트로 "조심해"라고 해봐야 실수 가능.

**Alternatives**: 요청 후 사후 검증. 기각 — 이미 전송된 정보는 회수 불가.

**Consequences**: researcher 에이전트는 PII 없는 일반 쿼리만 생성 가능. PII가 필요한 맞춤화는 로컬 합성으로 처리.

---

## ADR-004: writer ≠ reviewer 에이전트 분리 (다른 세션)
- 일자: 2026-04-14
- 상태: 채택

**Context**: 동일 에이전트가 작성과 리뷰를 동시에 하면 저자 편향으로 품질 저하. Mitchell Hashimoto 가이드 핵심.

**Decision**: writer 세션 완료 후 /clear → reviewer를 **새 세션**에서 실행. 리뷰 반영은 writer 세션으로 복귀하여 수행.

**Why**: 리뷰 때 신선한 눈 필요. 수정은 맥락 보존 필요. 두 요구 동시 충족 = 세션 분리.

**Alternatives**: 같은 세션 두 역할. 기각 — 컨텍스트 오염.

**Consequences**: UC-02 흐름에 /clear 명시. 리뷰 반영은 반드시 writer 세션(새 세션 금지).

---

## ADR-006: 초기 permissions는 Loose 모드 (G4 사용자 선택)
- 일자: 2026-04-14
- 상태: 채택

**Context**: G4 Decision Gate에서 사용자가 "느슨하게 — Git force push만 막기"를 선택.

**Decision**: deny는 force push / reset --hard만. evidence_vault/round immutability는 훅 **WARN 수준**으로 유지. PII MCP 가드는 BLOCK 유지(복구 불가 위험).

**Why**: 초기 실험 단계 유연성 확보. 실제 사용 중 실수 패턴 누적 시 단계적으로 permissions 강화 (기둥4 자기 진화).

**Consequences**: 하네스 엔지니어링 기둥3(도구 경계)가 이상적 수준보다 약함. 대신 훅 WARN으로 기둥4(피드백)는 유지. 실수 발생 시 permissions deny에 항목 추가로 즉시 강화 가능.

**회복 경로**: 실수 1건 → settings.local.json deny에 해당 패턴 추가 → 다음 세션부터 구조적 차단.

---

## ADR-005: 하네스 4기둥 + 3층 엔지니어링 통합
- 일자: 2026-04-14
- 상태: 채택

**Decision**: 프로젝트 자체가 프롬프트/컨텍스트/하네스 엔지니어링의 쇼케이스.
- 프롬프트 레이어: 학생 입력을 구조화 분해 (input/ 3종 강제)
- 컨텍스트 레이어: evidence_vault/research_cache/common 분리로 세션 로딩 효율화
- 하네스 레이어: 훅/permissions로 실수 구조 차단

**Why**: 요청자가 "프롬프트 개선도 수행하고 진행" 명시. 3층을 실제 구조로 체현.
