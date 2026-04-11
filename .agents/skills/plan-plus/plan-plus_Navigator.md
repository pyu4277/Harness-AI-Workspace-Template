# plan-plus -- Navigator

> SYSTEM_NAVIGATOR 스타일 시각적 네비게이터
> 최종 갱신: 2026-04-11 (Tier-C 신규 생성, Option E 세션 1)
> SKILL.md와 교차 참조 (이 파일은 SKILL.md의 시각화 계층)

---

## 0. 범례 + 사용법 {#범례--사용법}

### 상태 표시

| 표시 | 의미 |
|------|------|
| **[작동]** | 정상 작동 중 |
| **[부분]** | 일부만 작동 |
| **[미구현]** | 설계만 있고 구현 없음 |

### 다이어그램 규약

- ISO 5807:1985 표준 기호 준수
- Mermaid ELK 렌더러 + `securityLevel: loose`
- 점선 `-.->` = 피드백 루프 (재시도/복귀/거절 후 재진입)
- `:::warning` = 에러/차단/거절 블럭
- `click NODE "#anchor"` = 블럭 상세 카드로 이동

### 스킬 메타

| 항목 | 값 |
|------|-----|
| 이름 | plan-plus |
| Tier | C |
| 커맨드 | `/plan-plus [feature]` |
| 프로세스 타입 | Branching + Linear (7 Phase + HARD-GATE + 조건부 질문) |
| 설명 | Brainstorming Intent Discovery + bkit PDCA 결합. 의도 탐색 + 대안 비교 + YAGNI로 고품질 Plan 문서 생성 |

---

## 1. 전체 워크플로우 체계도 {#전체-체계도}

<!-- AUTO:DIAGRAM_MAIN:START -->

```mermaid
%%{init: {"flowchart": {"defaultRenderer": "elk"}, "securityLevel": "loose"} }%%
flowchart TD
    User([/plan-plus feature]):::io --> HardGate{HARD-GATE<br/>코드 작성 금지}

    HardGate --> P0[Phase 0<br/>Context Exploration<br/>자동]
    P0 --> P1[Phase 1<br/>Intent Discovery<br/>1 question at a time]

    P1 --> Q1[Q1 Core Purpose]
    Q1 --> Q2[Q2 Target Users]
    Q2 --> AmbigCheck{모호성<br/>높은가?}
    AmbigCheck -->|아니오| P2
    AmbigCheck -->|예| Q3[Q3 Success Criteria]
    Q3 --> Q4[Q4 Constraints<br/>선택]
    Q4 --> P2

    P2[Phase 2<br/>Alternatives<br/>2-3 approaches] --> Choose[/사용자가 선택/]
    Choose --> P3[Phase 3<br/>YAGNI Review<br/>multiSelect]
    P3 --> Defer[(deferred 항목<br/>Out of Scope)]
    Defer --> P4

    P4[Phase 4<br/>Incremental Validation<br/>section by section] --> S1{Architecture<br/>OK?}
    S1 -->|아니오| P4
    S1 -->|예| S2{Components<br/>OK?}
    S2 -->|아니오| P4
    S2 -->|예| S3{Data Flow<br/>OK?}
    S3 -->|아니오| P4
    S3 -->|예| P5[Phase 5<br/>Plan Document<br/>Generation]

    P5 --> Template[plan-plus.template.md]
    Template --> Doc[(`docs/01-plan/features/{feature}.plan.md`)]
    Doc --> ExecSum[Executive Summary<br/>4-perspective]
    ExecSum --> P6[Phase 6<br/>Next Steps]
    P6 --> NextSkill[`/pdca design {feature}` 안내]
    NextSkill --> EndOk([완료]):::io

    HardGate -.->|코드 작성 시도| Block[:::warning HARD-GATE 차단]:::warning
    Block -.-> HardGate

    click User "#node-user-call"
    click HardGate "#node-hard-gate"
    click P0 "#node-phase-0"
    click P1 "#node-phase-1"
    click Q1 "#node-q1"
    click Q2 "#node-q2"
    click AmbigCheck "#node-ambig-check"
    click Q3 "#node-q3"
    click Q4 "#node-q4"
    click P2 "#node-phase-2"
    click Choose "#node-choose"
    click P3 "#node-phase-3"
    click Defer "#node-defer"
    click P4 "#node-phase-4"
    click S1 "#node-section-arch"
    click S2 "#node-section-comp"
    click S3 "#node-section-flow"
    click P5 "#node-phase-5"
    click Template "#node-template"
    click Doc "#node-doc"
    click ExecSum "#node-exec-sum"
    click P6 "#node-phase-6"
    click NextSkill "#node-next-skill"
    click Block "#node-hard-gate-block"

    classDef warning fill:#fee,stroke:#c00,stroke-width:2px
    classDef io fill:#eef,stroke:#338,stroke-width:2px
```

> **패턴**: Branching + Linear -- 7 Phase 순차 흐름 + 각 Phase 내 조건부 분기. Phase 1은 모호성 판단으로 Q3/Q4 조건부 진입, Phase 4는 3개 섹션 각각 거절 시 재작성 루프. 전체를 HARD-GATE가 감싸 코드 작성을 차단.

<!-- AUTO:DIAGRAM_MAIN:END -->

<details><summary><strong>블럭 바로가기 (다이어그램 클릭 대안)</strong></summary>

[사용자 호출](#node-user-call) · [HARD-GATE](#node-hard-gate) · [Phase 0 Context](#node-phase-0) · [Phase 1 Intent](#node-phase-1) · [Q1 Core Purpose](#node-q1) · [Q2 Target Users](#node-q2) · [모호성 체크](#node-ambig-check) · [Q3 Success Criteria](#node-q3) · [Q4 Constraints](#node-q4) · [Phase 2 Alternatives](#node-phase-2) · [사용자 선택](#node-choose) · [Phase 3 YAGNI](#node-phase-3) · [deferred](#node-defer) · [Phase 4 Validation](#node-phase-4) · [Architecture 검증](#node-section-arch) · [Components 검증](#node-section-comp) · [Data Flow 검증](#node-section-flow) · [Phase 5 Generation](#node-phase-5) · [Template](#node-template) · [Plan Document](#node-doc) · [Executive Summary](#node-exec-sum) · [Phase 6 Next](#node-phase-6) · [pdca design 안내](#node-next-skill) · [HARD-GATE 차단](#node-hard-gate-block)
 · [**전체 블럭 카탈로그**](#block-catalog)

</details>

[맨 위로](#범례--사용법)

---

## 2. 블럭 상세 카탈로그 {#block-catalog}

<details><summary>블럭 카드 펼치기 (24개)</summary>

### 사용자 호출 {#node-user-call}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear 진입점 |
| 동기 | 모호하거나 복잡한 기획 요구사항을 체계적으로 탐색 |
| 내용 | `/plan-plus {feature}` 커맨드. 표준 `/pdca plan` 대신 브레인스토밍 강화 |
| 동작 방식 | argument-hint `[feature]`. 사용자가 기획할 기능명 전달 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### HARD-GATE {#node-hard-gate}

| 항목 | 내용 |
|------|------|
| 소속 | 전체 워크플로우 보호 게이트 |
| 동기 | Plan 승인 전 코드 작성 시작을 구조적으로 차단 |
| 내용 | "Do NOT write any code, scaffold any project, or invoke any implementation skill until this entire process is complete and the user has approved the Plan document." |
| 동작 방식 | LLM 자체 자제 + Stop hook(`plan-plus-stop.js`)이 전체 흐름 검증 |
| 상태 | [작동] |
| 관련 파일 | `.bkit/plugin/scripts/plan-plus-stop.js` |

[다이어그램으로 복귀](#전체-체계도)

### Phase 0: Context Exploration {#node-phase-0}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear Phase 1/7 (자동) |
| 동기 | 사용자에게 묻기 전에 프로젝트 상태를 자동 탐색하여 중복 질문 방지 |
| 내용 | CLAUDE.md/package.json/pom.xml 읽기 + 최근 5 git commit + `docs/01-plan/` 기존 문서 확인 + `.bkit-memory.json` 확인 |
| 동작 방식 | 도구 호출 4종 자동 실행 후 한 줄 요약 출력 |
| 상태 | [작동] |
| 관련 파일 | `CLAUDE.md`, `.bkit-memory.json`, `docs/01-plan/` |

[다이어그램으로 복귀](#전체-체계도)

### Phase 1: Intent Discovery {#node-phase-1}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear Phase 2/7 (대화형) |
| 동기 | 사용자의 진짜 의도를 1 question at a time으로 정밀 추출 |
| 내용 | Q1~Q4 순차 진행. 명확한 기능은 Q1-Q2만, 모호하면 Q3-Q4까지 |
| 동작 방식 | AskUserQuestion 도구로 1개씩 묻기. 다중 선택 우선, custom 옵션 항상 포함 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Q1: Core Purpose {#node-q1}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 1 첫 질문 (필수) |
| 동기 | 기능이 해결하는 핵심 문제 정의 |
| 내용 | "What is the core problem this feature solves?" + 3-4 보기 (프로젝트 컨텍스트에서 추론) |
| 동작 방식 | AskUserQuestion 호출. options 3-4 + custom 입력 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Q2: Target Users {#node-q2}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 1 두 번째 질문 (필수) |
| 동기 | 사용자 페르소나 명확화로 디자인 우선순위 결정 |
| 내용 | "Who will primarily use this feature?" + Admin/End user/Developer/External system |
| 동작 방식 | AskUserQuestion 호출. multiSelect 가능 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 모호성 체크 {#node-ambig-check}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 1 분기 결정 |
| 동기 | 명확한 기능에 불필요한 질문을 강요하지 않음 (질문 최소화) |
| 내용 | Q1-Q2 답변이 충분히 구체적이면 Q3-Q4 스킵, 아니면 진행 |
| 동작 방식 | LLM 판단 (휴리스틱). 답변에 측정 가능한 기준이 있으면 충분 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Q3: Success Criteria {#node-q3}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 1 조건부 질문 (모호 시) |
| 동기 | 측정 가능한 성공 기준 도출 |
| 내용 | "What criteria would indicate this feature is successful?" |
| 동작 방식 | AskUserQuestion 호출. 구체적이고 측정 가능한 기준 유도 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Q4: Constraints {#node-q4}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 1 조건부 질문 (필요 시) |
| 동기 | 기존 시스템 충돌 / 성능 / 기술 제약 사전 파악 |
| 내용 | 충돌, 성능 요구, 기술 제약 등 |
| 동작 방식 | AskUserQuestion 호출. 자유 입력 또는 카테고리 선택 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Phase 2: Alternatives Exploration {#node-phase-2}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear Phase 3/7 (브레인스토밍 핵심) |
| 동기 | 단일 해결책 함정 방지. 항상 2-3 대안 비교 |
| 내용 | Approach A (Recommended) + B + C(선택) 각각 Pros/Cons/Best for |
| 동작 방식 | LLM이 대안 생성 → 마크다운 출력 → AskUserQuestion으로 선택 받기 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 사용자 선택 {#node-choose}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 2 출구 |
| 동기 | 여러 대안 중 사용자가 직접 선택하여 의사결정 명시 |
| 내용 | 선택된 approach가 Phase 3-5의 기준이 됨 |
| 동작 방식 | AskUserQuestion 호출. options=approaches |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Phase 3: YAGNI Review {#node-phase-3}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear Phase 4/7 (브레인스토밍 핵심) |
| 동기 | "지금 필요하지 않은 것은 만들지 말라" 원칙으로 첫 버전 minimal 보장 |
| 내용 | 선택된 approach의 모든 기능 나열 → multiSelect로 essential만 선택 |
| 동작 방식 | AskUserQuestion 호출. multiSelect: true. 미선택 항목은 Out of Scope으로 분리 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### deferred 항목 {#node-defer}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 3 출력 |
| 동기 | 선택되지 않은 기능을 명시적으로 보존 (향후 참조용) |
| 내용 | Out of Scope 섹션으로 Plan 문서에 기록 |
| 동작 방식 | YAGNI 결과의 미선택 항목 자동 수집 |
| 상태 | [작동] |
| 관련 파일 | `docs/01-plan/features/{feature}.plan.md` |

[다이어그램으로 복귀](#전체-체계도)

### Phase 4: Incremental Design Validation {#node-phase-4}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear Phase 5/7 (브레인스토밍 핵심) |
| 동기 | 거대한 디자인을 한 번에 승인받는 대신 섹션별 점진 검증으로 거절 비용 최소화 |
| 내용 | 3개 섹션 (Architecture/Components/Data Flow) 각각 승인 절차 |
| 동작 방식 | 섹션 출력 → 사용자 OK 응답 → 다음 섹션. 거절 시 해당 섹션만 수정 후 재제시 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Architecture 검증 {#node-section-arch}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 4 섹션 1/3 |
| 동기 | 전체 구조의 방향성 확인 (계층/모듈 구분/외부 연동) |
| 내용 | "Does this direction look right?" |
| 동작 방식 | 마크다운 출력 → 거절 시 architecture만 재작성 → 재제시 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Components 검증 {#node-section-comp}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 4 섹션 2/3 |
| 동기 | 핵심 컴포넌트/모듈 구조 합의 |
| 내용 | "Does this structure look right?" |
| 동작 방식 | 마크다운 출력 → 거절 시 components만 재작성 → 재제시 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Data Flow 검증 {#node-section-flow}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 4 섹션 3/3 |
| 동기 | 데이터 흐름 합의로 implementation 단계 가속 |
| 내용 | "Does this flow look right?" |
| 동작 방식 | 마크다운 출력 → 거절 시 data flow만 재작성 → 재제시 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Phase 5: Plan Document Generation {#node-phase-5}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear Phase 6/7 (출력) |
| 동기 | Phase 0-4 결과를 단일 Plan 문서로 통합 |
| 내용 | plan-plus.template.md 기반 생성 + 표준 plan과 다른 추가 섹션 5종 |
| 동작 방식 | 템플릿 변수 치환 → Write 도구로 파일 생성 → PDCA 상태 갱신 |
| 상태 | [작동] |
| 관련 파일 | `.agents/templates/plan-plus.template.md`, `.bkit-memory.json` |

[다이어그램으로 복귀](#전체-체계도)

### Template {#node-template}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 5 입력 |
| 동기 | 표준 형식 보장 + 변수 치환 가능 |
| 내용 | plan-plus.template.md (User Intent Discovery / Alternatives Explored / YAGNI Review / Brainstorming Log / Executive Summary 섹션 포함) |
| 동작 방식 | Read 도구로 로드 → 변수 치환 → Write |
| 상태 | [작동] |
| 관련 파일 | `.agents/templates/plan-plus.template.md` |

[다이어그램으로 복귀](#전체-체계도)

### Plan Document {#node-doc}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 5 출력 |
| 동기 | 후속 PDCA 단계의 단일 진실 원천 |
| 내용 | Phase 0-4 결과 + Executive Summary + 표준 plan 섹션 |
| 동작 방식 | Write to `docs/01-plan/features/{feature}.plan.md` |
| 상태 | [작동] |
| 관련 파일 | `docs/01-plan/features/{feature}.plan.md` |

[다이어그램으로 복귀](#전체-체계도)

### Executive Summary {#node-exec-sum}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 5 핵심 섹션 |
| 동기 | 사용자가 파일을 열지 않아도 4관점 요약을 즉시 확인 |
| 내용 | Problem / Solution / Function UX Effect / Core Value 4 perspective |
| 동작 방식 | LLM이 Phase 1-4 결과 자동 합성 → 표 형식 → 응답에도 출력 (MANDATORY) |
| 상태 | [작동] |
| 관련 파일 | `docs/01-plan/features/{feature}.plan.md` |

[다이어그램으로 복귀](#전체-체계도)

### Phase 6: Next Steps {#node-phase-6}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear Phase 7/7 (출구) |
| 동기 | 표준 PDCA 사이클로 자연스럽게 핸드오프 |
| 내용 | "Plan Plus completed" + Document path + Next step 안내 |
| 동작 방식 | 출력만 (state는 이미 Phase 5에서 갱신) |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/plan-plus/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### pdca design 안내 {#node-next-skill}

| 항목 | 내용 |
|------|------|
| 소속 | Phase 6 외부 트리거 |
| 동기 | 사용자가 다음 스킬을 명시적으로 호출하도록 안내 (자동 호출 금지) |
| 내용 | "Next step: /pdca design {feature}" |
| 동작 방식 | 텍스트 출력. next-skill: pdca design (frontmatter 참조) |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### HARD-GATE 차단 {#node-hard-gate-block}

| 항목 | 내용 |
|------|------|
| 소속 | HARD-GATE 위반 시 차단 분기 |
| 동기 | Plan 미승인 상태에서 코드/스캐폴드/구현 스킬 호출 시도를 즉시 차단 |
| 내용 | 차단 메시지 + 현재 Phase 안내 + Plan 승인 필요 |
| 동작 방식 | LLM 자체 자제 + Stop hook 검증 (`plan-plus-stop.js` 10초 timeout) |
| 상태 | [작동] |
| 관련 파일 | `.bkit/plugin/scripts/plan-plus-stop.js` |

[다이어그램으로 복귀](#전체-체계도)

</details>

[맨 위로](#범례--사용법)

---

## 3. 사용 시나리오

### 시나리오 1: 모호한 요구사항 정밀 탐색

```
사용자: /plan-plus user-authentication
plan-plus:
  Phase 0: 프로젝트 상태 탐색 완료 (Next.js + PostgreSQL, 신규 기능)
  Phase 1 Q1: 인증의 핵심 문제는 무엇인가요?
    [a] 비밀번호 분실 [b] OAuth 통합 [c] 세션 만료 [d] custom
  사용자: [b]
  Phase 1 Q2: 주 사용자는?
    [a] 일반 사용자 [b] 관리자 [c] 외부 시스템
  사용자: [a]
  → 모호성 낮음 → Q3-Q4 스킵
  Phase 2: Approach A (NextAuth.js, 권장) / B (Supabase Auth) / C (custom JWT)
  사용자: A
  Phase 3 YAGNI: 첫 버전에 필요한 항목 multiSelect
    [O] Google 로그인  [O] 세션 관리  [-] MFA  [-] 이메일 인증
  Phase 4: Architecture → Components → Data Flow 각각 OK
  Phase 5: docs/01-plan/features/user-authentication.plan.md 생성
  Phase 6: Next: /pdca design user-authentication
```

### 시나리오 2: 명확한 기능 빠른 처리

```
사용자: /plan-plus dark-mode-toggle
plan-plus:
  Phase 0: ...
  Phase 1 Q1: 핵심 문제? → [b] 야간 가독성
  Phase 1 Q2: 주 사용자? → [a] 일반 사용자
  → Q3-Q4 스킵 (충분히 명확)
  Phase 2: A (CSS variables) / B (next-themes 라이브러리)
  사용자: B
  Phase 3 YAGNI: [O] 토글 버튼 [O] localStorage 저장 [-] 시스템 설정 동기화
  Phase 4: 3 섹션 모두 한 번에 OK
  Phase 5: 문서 생성
```

### 시나리오 3: HARD-GATE 위반 시도 차단

```
사용자: /plan-plus payment-integration
plan-plus: Phase 0 완료. Phase 1 시작...
사용자: 그냥 Stripe SDK 코드 작성해줘
plan-plus: HARD-GATE 차단. Plan 문서 승인 전에는 코드 작성 불가.
  현재 Phase 1 (Intent Discovery) 진행 중. Q1부터 답변 부탁드립니다.
```

[맨 위로](#범례--사용법)

---

## 4. 제약사항

- **HARD-GATE**: Plan 승인 전 코드/스캐폴드/구현 스킬 호출 불가. 단순해 보이는 기능도 동일 적용
- **Phase 건너뛰기 금지**: Phase 0-6 순차 진행. Phase 1만 모호성 판단으로 Q3-Q4 조건부 스킵 가능
- **AskUserQuestion 강제**: Phase 1/2/3에서 사용자 응답 없이 임의 결정 금지
- **2-3 대안 강제**: Phase 2에서 1개 대안만 제시 금지 (브레인스토밍 원칙)
- **YAGNI 강제**: Phase 3 multiSelect 결과를 무시하고 모든 기능 포함 금지
- **이모티콘 금지**: 표 마커는 ASCII만 (IMP-021)
- **절대경로 금지**: 모든 경로는 프로젝트 루트 상대경로
- **Stop hook 통합**: `plan-plus-stop.js`가 세션 종료 시 자동 검증 (10초 timeout)
- **표준 PDCA 호환**: 출력 문서는 표준 plan과 동일 위치/형식 → `/pdca design` 자연 연결
- **단순 작업 부적합**: 코드 변경만 필요한 작업, 명확한 버그 수정 등은 plan-plus 사용 금지

[맨 위로](#범례--사용법)

---

## 5. 갱신 이력

| 날짜 | 변경 | 트리거 |
|------|------|--------|
| 2026-04-11 | Tier-C 신규 생성 (Branching + Linear 7 Phase + HARD-GATE + 24 블럭 카드 + Mermaid) | Option E 세션 1 |

[맨 위로](#범례--사용법)
