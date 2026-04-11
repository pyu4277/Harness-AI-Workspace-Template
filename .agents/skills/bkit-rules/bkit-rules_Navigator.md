# bkit-rules -- Navigator

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
- 점선 `-.->` = 자동 적용 / 수동 오버라이드
- `:::warning` = 차단/거절 분기
- `click NODE "#anchor"` = 블럭 상세 카드로 이동

### 스킬 메타

| 항목 | 값 |
|------|-----|
| 이름 | bkit-rules |
| Tier | C |
| 커맨드 | 자동 로드 (user-invocable: false) |
| 프로세스 타입 | Branching + Linear (9 규칙 섹션 + 다중 자동 분기) |
| 설명 | bkit 플러그인 자동 적용 규칙. PDCA 적용 + 레벨 감지 + Agent 자동 호출 + 코드 품질 + Task 분류 |

---

## 1. 전체 워크플로우 체계도 {#전체-체계도}

<!-- AUTO:DIAGRAM_MAIN:START -->

```mermaid
%%{init: {"flowchart": {"defaultRenderer": "elk"}, "securityLevel": "loose"} }%%
flowchart TD
    Req([사용자 요청]):::io --> R1[1. PDCA Auto-Apply<br/>요청 타입 분류]

    R1 --> ReqType{요청 타입}
    ReqType -->|new feature| CheckDesign[design 문서 확인]
    ReqType -->|bug fix| Compare[code + design 비교]
    ReqType -->|refactoring| Analyze[현황 분석 + plan]
    ReqType -->|impl complete| GapSuggest[Gap 분석 제안]

    CheckDesign --> R2[2. Level Auto-Detection]
    Compare --> R2
    Analyze --> R2
    GapSuggest --> R2

    R2 --> LevelCheck{Level 판정}
    LevelCheck -->|2+ enterprise 조건| Enterprise[Enterprise<br/>4 teammates]
    LevelCheck -->|1+ dynamic 조건| Dynamic[Dynamic<br/>2 teammates]
    LevelCheck -->|none| Starter[Starter<br/>친절 모드]

    Enterprise --> R3[3. Agent Auto-Trigger]
    Dynamic --> R3
    Starter --> R3

    R3 --> TaskKw{Task 키워드}
    TaskKw -->|review| InvokeReview[bkit:code-analyzer]
    TaskKw -->|design check| InvokeDesign[bkit:design-validator]
    TaskKw -->|gap| InvokeGap[bkit:gap-detector]
    TaskKw -->|report| InvokeReport[bkit:report-generator]
    TaskKw -->|QA logs| InvokeQA[bkit:qa-monitor]
    TaskKw -->|기타| R4

    InvokeReview --> R4[4. Code Quality]
    InvokeDesign --> R4
    InvokeGap --> R4
    InvokeReport --> R4
    InvokeQA --> R4

    R4 --> SearchExist{기존 코드<br/>존재?}
    SearchExist -->|예| Reuse[재사용]
    SearchExist -->|아니오| Create[신규 작성<br/>DRY/SRP 준수]

    Reuse --> R5[5. Task Classification]
    Create --> R5

    R5 --> SizeClass{내용 크기}
    SizeClass -->|< 50 chars| QuickFix[Quick Fix<br/>즉시 실행]
    SizeClass -->|50-200| MinorChange[Minor Change<br/>요약 후 진행]
    SizeClass -->|200-1000| Feature[Feature<br/>design 확인/생성]
    SizeClass -->|> 1000| MajorFeat[Major Feature<br/>design + 사용자 확인]

    QuickFix --> R6[6. Output Style]
    MinorChange --> R6
    Feature --> R6
    MajorFeat --> R6

    R6 --> StyleMatch{Level별 매칭}
    StyleMatch -->|Starter| StyleLearn[bkit-learning]
    StyleMatch -->|Dynamic| StylePdca[bkit-pdca-guide]
    StyleMatch -->|Enterprise| StyleEnt[bkit-enterprise]

    StyleLearn --> R7[7. Agent Teams Suggestion]
    StylePdca --> R7
    StyleEnt --> R7

    R7 --> TeamCheck{Major + Dynamic+?}
    TeamCheck -->|예| SuggestTeam[/pdca team 제안]
    TeamCheck -->|아니오| R8[8. Agent Memory<br/>자동 활성]

    SuggestTeam --> R8
    R8 --> R9[9. Plugin Hot Reload<br/>안내]
    R9 --> EndOk([적용 완료]):::io

    click Req "#node-user-req"
    click R1 "#node-r1-pdca"
    click ReqType "#node-req-type"
    click CheckDesign "#node-check-design"
    click Compare "#node-compare"
    click Analyze "#node-analyze-current"
    click GapSuggest "#node-gap-suggest"
    click R2 "#node-r2-level"
    click LevelCheck "#node-level-check"
    click Enterprise "#node-enterprise"
    click Dynamic "#node-dynamic"
    click Starter "#node-starter"
    click R3 "#node-r3-agent"
    click TaskKw "#node-task-kw"
    click InvokeReview "#node-invoke-review"
    click InvokeDesign "#node-invoke-design"
    click InvokeGap "#node-invoke-gap"
    click InvokeReport "#node-invoke-report"
    click InvokeQA "#node-invoke-qa"
    click R4 "#node-r4-quality"
    click SearchExist "#node-search-exist"
    click Reuse "#node-reuse"
    click Create "#node-create-new"
    click R5 "#node-r5-task"
    click SizeClass "#node-size-class"
    click QuickFix "#node-quick-fix"
    click MinorChange "#node-minor-change"
    click Feature "#node-feature"
    click MajorFeat "#node-major-feat"
    click R6 "#node-r6-style"
    click StyleMatch "#node-style-match"
    click StyleLearn "#node-style-learn"
    click StylePdca "#node-style-pdca"
    click StyleEnt "#node-style-ent"
    click R7 "#node-r7-teams"
    click TeamCheck "#node-team-check"
    click SuggestTeam "#node-suggest-team"
    click R8 "#node-r8-memory"
    click R9 "#node-r9-reload"

    classDef warning fill:#fee,stroke:#c00,stroke-width:2px
    classDef io fill:#eef,stroke:#338,stroke-width:2px
```

> **패턴**: Branching + Linear -- 9 규칙 섹션이 순차적으로 적용되지만, 각 섹션이 자체 분기를 포함. R2(Level)/R3(Task)/R5(Size)/R6(Style)이 핵심 분기 포인트. 모든 분기는 다음 규칙으로 수렴되어 단일 출구로 통합.

<!-- AUTO:DIAGRAM_MAIN:END -->

<details><summary><strong>블럭 바로가기 (다이어그램 클릭 대안)</strong></summary>

[사용자 요청](#node-user-req) · [R1 PDCA Auto-Apply](#node-r1-pdca) · [요청 타입 분기](#node-req-type) · [design 확인](#node-check-design) · [code+design 비교](#node-compare) · [현황 분석](#node-analyze-current) · [Gap 제안](#node-gap-suggest) · [R2 Level Detection](#node-r2-level) · [Level 판정](#node-level-check) · [Enterprise](#node-enterprise) · [Dynamic](#node-dynamic) · [Starter](#node-starter) · [R3 Agent Auto-Trigger](#node-r3-agent) · [Task 키워드](#node-task-kw) · [code-analyzer](#node-invoke-review) · [design-validator](#node-invoke-design) · [gap-detector](#node-invoke-gap) · [report-generator](#node-invoke-report) · [qa-monitor](#node-invoke-qa) · [R4 Code Quality](#node-r4-quality) · [기존 코드 검색](#node-search-exist) · [재사용](#node-reuse) · [신규 작성](#node-create-new) · [R5 Task Classification](#node-r5-task) · [내용 크기 분기](#node-size-class) · [Quick Fix](#node-quick-fix) · [Minor Change](#node-minor-change) · [Feature](#node-feature) · [Major Feature](#node-major-feat) · [R6 Output Style](#node-r6-style) · [Level별 매칭](#node-style-match) · [bkit-learning](#node-style-learn) · [bkit-pdca-guide](#node-style-pdca) · [bkit-enterprise](#node-style-ent) · [R7 Agent Teams](#node-r7-teams) · [Team 조건 체크](#node-team-check) · [team 제안](#node-suggest-team) · [R8 Agent Memory](#node-r8-memory) · [R9 Plugin Hot Reload](#node-r9-reload)
 · [**전체 블럭 카탈로그**](#block-catalog)

</details>

[맨 위로](#범례--사용법)

---

## 2. 블럭 상세 카탈로그 {#block-catalog}

<details><summary>블럭 카드 펼치기 (29개)</summary>

### 사용자 요청 {#node-user-req}

| 항목 | 내용 |
|------|------|
| 소속 | Branching + Linear 진입점 |
| 동기 | 사용자가 명시 호출하지 않아도 자동으로 9 규칙 적용 |
| 내용 | 기능 개발/코드 변경/구현 작업 요청 시 자동 트리거 |
| 동작 방식 | user-invocable: false. bkit 환경에서 항상 활성. trigger 키워드 매칭 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/bkit-rules/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 1. PDCA Auto-Apply {#node-r1-pdca}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 1/9 (PDCA 자동 적용) |
| 동기 | "No Guessing" + "SoR Priority" 원칙으로 추측 기반 작업 차단 |
| 내용 | Code > CLAUDE.md > docs/ design 문서 우선순위. 요청 타입별 행동 표 |
| 동작 방식 | LLM이 요청을 분류 → 매칭된 행동 실행 (design 확인/비교/분석/제안) |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/`, `CLAUDE.md` |

[다이어그램으로 복귀](#전체-체계도)

### 요청 타입 분기 {#node-req-type}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 1 분기 결정 |
| 동기 | 요청 타입에 따라 다른 행동 |
| 내용 | new feature / bug fix / refactoring / implementation complete 4종 |
| 동작 방식 | 키워드 매칭 + 컨텍스트 분석 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/bkit-rules/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### design 문서 확인 {#node-check-design}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 1 → new feature 분기 |
| 동기 | 신규 기능은 design 문서 없이 구현 금지 |
| 내용 | `docs/02-design/` 확인 → 없으면 design 먼저 |
| 동작 방식 | Glob/Read 도구로 문서 존재 확인 |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/` |

[다이어그램으로 복귀](#전체-체계도)

### code + design 비교 {#node-compare}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 1 → bug fix 분기 |
| 동기 | 버그가 코드 문제인지 design 문제인지 구분 |
| 내용 | 현재 동작 vs 의도된 동작 비교 후 수정 |
| 동작 방식 | Read 코드 + Read design → 차이 분석 |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/`, 코드 |

[다이어그램으로 복귀](#전체-체계도)

### 현황 분석 + plan {#node-analyze-current}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 1 → refactoring 분기 |
| 동기 | 무계획 리팩토링 금지 |
| 내용 | 현재 분석 → plan → design 갱신 → 실행 |
| 동작 방식 | 4단계 순차 진행. plan 중 사용자 확인 |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/` |

[다이어그램으로 복귀](#전체-체계도)

### Gap 분석 제안 {#node-gap-suggest}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 1 → implementation complete 분기 |
| 동기 | 구현 완료 후 design과의 차이 자동 감지 |
| 내용 | "Suggest Gap analysis" |
| 동작 방식 | bkit:gap-detector 호출 제안 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/gap-detector.md` |

[다이어그램으로 복귀](#전체-체계도)

### 2. Level Auto-Detection {#node-r2-level}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 2/9 (레벨 자동 감지) |
| 동기 | 프로젝트 규모에 맞는 행동/문서 수준 자동 조정 |
| 내용 | 1순위 CLAUDE.md 명시 → 2순위 파일 구조 감지 |
| 동작 방식 | Read CLAUDE.md → Glob 파일 구조 → 조건 매칭 |
| 상태 | [작동] |
| 관련 파일 | `CLAUDE.md`, 프로젝트 루트 구조 |

[다이어그램으로 복귀](#전체-체계도)

### Level 판정 {#node-level-check}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 2 분기 결정 |
| 동기 | 3-tier 분류로 행동 양식 결정 |
| 내용 | Enterprise (2+ 조건) / Dynamic (1+ 조건) / Starter (none) |
| 동작 방식 | 우선순위: Enterprise > Dynamic > Starter |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/bkit-rules/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Enterprise (4 teammates) {#node-enterprise}

| 항목 | 내용 |
|------|------|
| 소속 | Level 분기 → Enterprise |
| 동기 | 마이크로서비스/터보레포/k8s 등 대규모 시스템 |
| 내용 | infra/terraform/, infra/k8s/, services/ (2+), turbo.json, docker-compose.yml, .github/workflows/ 중 2+ 조건 |
| 동작 방식 | 간결 설명 + 아키텍처 코멘트 + enterprise-expert agent + 4 teammates |
| 상태 | [작동] |
| 관련 파일 | `.agents/agents/bkit/enterprise-expert.md` |

[다이어그램으로 복귀](#전체-체계도)

### Dynamic (2 teammates) {#node-dynamic}

| 항목 | 내용 |
|------|------|
| 소속 | Level 분기 → Dynamic |
| 동기 | 백엔드/DB 사용 풀스택 앱 |
| 내용 | bkend in .mcp.json, lib/bkend/, supabase/, firebase.json 중 1+ |
| 동작 방식 | 기술적 명확 설명 + bkend-expert agent + 2 teammates |
| 상태 | [작동] |
| 관련 파일 | `.agents/agents/bkit/bkend-expert.md` |

[다이어그램으로 복귀](#전체-체계도)

### Starter (친절 모드) {#node-starter}

| 항목 | 내용 |
|------|------|
| 소속 | Level 분기 → Starter |
| 동기 | 학습자/신규 프로젝트에 친화적 응답 |
| 내용 | 위 조건 모두 미충족 |
| 동작 방식 | 친절 설명 + 자세한 코멘트 + starter-guide agent (memory: user) |
| 상태 | [작동] |
| 관련 파일 | `.agents/agents/bkit/starter-guide.md` |

[다이어그램으로 복귀](#전체-체계도)

### 3. Agent Auto-Trigger {#node-r3-agent}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 3/9 (Agent 자동 호출) |
| 동기 | 사용자가 agent를 명시 호출하지 않아도 자동 트리거 |
| 내용 | Level 기반 + Task 기반 두 축. Task 키워드 → 매칭된 agent |
| 동작 방식 | LLM이 사용자 의도 분류 → agent 호출 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/` |

[다이어그램으로 복귀](#전체-체계도)

### Task 키워드 분기 {#node-task-kw}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 3 분기 결정 |
| 동기 | 6가지 Task 의도 자동 인식 |
| 내용 | code review / design check / gap / report / QA logs / 기타 |
| 동작 방식 | 키워드 매칭 → agent 매핑 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/bkit-rules/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### bkit:code-analyzer {#node-invoke-review}

| 항목 | 내용 |
|------|------|
| 소속 | Task 분기 → review/security |
| 동기 | 코드 품질 + 보안 검사 자동화 |
| 내용 | "code review", "security scan" 키워드 |
| 동작 방식 | code-analyzer agent 호출 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/code-analyzer.md` |

[다이어그램으로 복귀](#전체-체계도)

### bkit:design-validator {#node-invoke-design}

| 항목 | 내용 |
|------|------|
| 소속 | Task 분기 → design check |
| 동기 | design 문서 검증 자동화 |
| 내용 | "design review", "spec check" 키워드 |
| 동작 방식 | design-validator agent 호출 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/design-validator.md` |

[다이어그램으로 복귀](#전체-체계도)

### bkit:gap-detector {#node-invoke-gap}

| 항목 | 내용 |
|------|------|
| 소속 | Task 분기 → gap analysis |
| 동기 | 구현 vs design Gap 자동 감지 |
| 내용 | "gap analysis" 키워드 |
| 동작 방식 | gap-detector agent 호출 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/gap-detector.md` |

[다이어그램으로 복귀](#전체-체계도)

### bkit:report-generator {#node-invoke-report}

| 항목 | 내용 |
|------|------|
| 소속 | Task 분기 → report |
| 동기 | 보고서/요약 자동 생성 |
| 내용 | "report", "summary" 키워드 |
| 동작 방식 | report-generator agent 호출 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/report-generator.md` |

[다이어그램으로 복귀](#전체-체계도)

### bkit:qa-monitor {#node-invoke-qa}

| 항목 | 내용 |
|------|------|
| 소속 | Task 분기 → QA |
| 동기 | QA + 로그 분석 자동화 |
| 내용 | "QA", "log analysis" 키워드 |
| 동작 방식 | qa-monitor agent 호출 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/qa-monitor.md` |

[다이어그램으로 복귀](#전체-체계도)

### 4. Code Quality {#node-r4-quality}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 4/9 (코드 품질 표준) |
| 동기 | 코딩 전 기존 코드 검색 + DRY/SRP/No Hardcoding 강제 |
| 내용 | Pre-coding 검색 + Self-check + Refactor 트리거 |
| 동작 방식 | 4가지 자가 점검 (logic 중복, 재사용, 하드코딩, 단일 책임) |
| 상태 | [작동] |
| 관련 파일 | `utils/`, `hooks/`, `components/ui/` |

[다이어그램으로 복귀](#전체-체계도)

### 기존 코드 검색 {#node-search-exist}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 4 → Pre-coding 단계 |
| 동기 | 중복 구현 방지 (DRY) |
| 내용 | Glob/Grep으로 utils, hooks, components 검색 |
| 동작 방식 | 검색 결과에 따라 Reuse 또는 Create 분기 |
| 상태 | [작동] |
| 관련 파일 | 프로젝트 전체 |

[다이어그램으로 복귀](#전체-체계도)

### 재사용 {#node-reuse}

| 항목 | 내용 |
|------|------|
| 소속 | Code Quality → Reuse 분기 |
| 동기 | 기존 함수 재사용으로 일관성 확보 |
| 내용 | import + 호출 |
| 동작 방식 | Read 기존 함수 시그니처 → import → 호출 |
| 상태 | [작동] |
| 관련 파일 | 프로젝트 코드 |

[다이어그램으로 복귀](#전체-체계도)

### 신규 작성 {#node-create-new}

| 항목 | 내용 |
|------|------|
| 소속 | Code Quality → Create 분기 |
| 동기 | 없는 기능을 일반화 패턴으로 신규 작성 |
| 내용 | DRY/SRP/No Hardcoding/Extensibility 4 원칙 준수 |
| 동작 방식 | 작성 후 Self-check 4가지 적용. Refactor 트리거 (20줄 초과/3+ nest/2회 중복) |
| 상태 | [작동] |
| 관련 파일 | 프로젝트 코드 |

[다이어그램으로 복귀](#전체-체계도)

### 5. Task Classification {#node-r5-task}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 5/9 (Task 분류) |
| 동기 | 작업 크기에 맞는 PDCA 레벨 자동 적용 (오버킬 방지) |
| 내용 | 4 분류 (Quick Fix / Minor / Feature / Major) + 키워드 매핑 |
| 동작 방식 | 사용자 요청 길이 + 키워드 매칭 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/bkit-rules/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 내용 크기 분기 {#node-size-class}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 5 분기 결정 |
| 동기 | 글자수 + 키워드 → PDCA 레벨 결정 |
| 내용 | < 50 / 50-200 / 200-1000 / > 1000 chars |
| 동작 방식 | 길이 측정 + 키워드 fallback |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/bkit-rules/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Quick Fix {#node-quick-fix}

| 항목 | 내용 |
|------|------|
| 소속 | Task 크기 → < 50 chars |
| 동기 | 오타/사소한 수정에 PDCA 강제 안 함 |
| 내용 | PDCA Level: None. 즉시 실행 |
| 동작 방식 | 직접 Edit 도구 호출 |
| 상태 | [작동] |
| 관련 파일 | 변경 대상 |

[다이어그램으로 복귀](#전체-체계도)

### Minor Change {#node-minor-change}

| 항목 | 내용 |
|------|------|
| 소속 | Task 크기 → 50-200 chars |
| 동기 | 가벼운 개선은 요약 후 즉시 진행 |
| 내용 | PDCA Level: Lite. 요약 → 진행 |
| 동작 방식 | 간단 설명 + Edit 도구 |
| 상태 | [작동] |
| 관련 파일 | 변경 대상 |

[다이어그램으로 복귀](#전체-체계도)

### Feature {#node-feature}

| 항목 | 내용 |
|------|------|
| 소속 | Task 크기 → 200-1000 chars |
| 동기 | 신규 기능은 design 문서 필수 |
| 내용 | PDCA Level: Standard. design 확인/생성 |
| 동작 방식 | docs/02-design/ 확인 → 없으면 생성 → 구현 |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/` |

[다이어그램으로 복귀](#전체-체계도)

### Major Feature {#node-major-feat}

| 항목 | 내용 |
|------|------|
| 소속 | Task 크기 → > 1000 chars |
| 동기 | 대형 변경은 사용자 확인 + 엄격한 design 필수 |
| 내용 | PDCA Level: Strict. design 필수 + 사용자 확인 |
| 동작 방식 | design 작성 → 사용자 승인 → 구현 (HARD-GATE 유사) |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/` |

[다이어그램으로 복귀](#전체-체계도)

### 6. Output Style Auto-Selection {#node-r6-style}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 6/9 (출력 스타일 자동 선택, v1.5.1) |
| 동기 | Level에 맞는 응답 스타일을 자동 제안 |
| 내용 | Starter → bkit-learning, Dynamic → bkit-pdca-guide, Enterprise → bkit-enterprise |
| 동작 방식 | 세션 시작 + level init + PDCA 전환 시 트리거. `/output-style`로 사용자 오버라이드 가능 |
| 상태 | [작동] |
| 관련 파일 | `.claude/output-styles/bkit-*.md` |

[다이어그램으로 복귀](#전체-체계도)

### 7. Agent Teams Suggestion {#node-r7-teams}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 7/9 (Agent Teams 제안, v1.5.1) |
| 동기 | 대형 작업에서 병렬 PDCA 가속 |
| 내용 | Major Feature + Dynamic/Enterprise 조합에서 `/pdca team` 제안 |
| 동작 방식 | 조건 매칭 → 텍스트 제안. `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경변수 필요 |
| 상태 | [부분] (실험 기능, env 미설정 시 안내만) |
| 관련 파일 | `.agents/skills/bkit-rules/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 8. Agent Memory {#node-r8-memory}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 8/9 (Agent Memory 자동 활성, v1.5.1) |
| 동기 | 세션 간 컨텍스트 보존으로 반복 설명 제거 |
| 내용 | project scope (9 agents) + user scope (2 agents: starter-guide, pipeline-guide) |
| 동작 방식 | 자동. `.claude/agent-memory/` (project) 또는 `~/.claude/agent-memory/` (user)에 영속 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agent-memory/` |

[다이어그램으로 복귀](#전체-체계도)

### 9. Plugin Hot Reload {#node-r9-reload}

| 항목 | 내용 |
|------|------|
| 소속 | 규칙 9/9 (플러그인 핫 리로드, v1.6.0) |
| 동기 | bkit 플러그인 수정 후 세션 재시작 없이 적용 |
| 내용 | `/reload-plugins` 커맨드. skills/agents/hooks/templates 즉시 반영 |
| 동작 방식 | 핫 리로드 트리거. CLAUDE.md 변경은 별도 `/clear` 필요 |
| 상태 | [작동] |
| 관련 파일 | `.claude/commands/reload-plugins.md` |

[다이어그램으로 복귀](#전체-체계도)

</details>

[맨 위로](#범례--사용법)

---

## 3. 사용 시나리오

### 시나리오 1: 신규 기능 요청 자동 처리

```
사용자: "다크 모드 토글 추가해줘"
bkit-rules 자동 적용:
  R1: new feature → docs/02-design/dark-mode.md 확인 (없음)
  R5: 200-500 chars → Feature → design 먼저 생성
  R2: lib/bkend/ 발견 → Dynamic Level
  R6: bkit-pdca-guide 스타일 자동 제안
  → Claude는 design 문서를 먼저 작성하고 사용자에게 확인 후 구현
```

### 시나리오 2: 대형 마이그레이션 요청 자동 차단

```
사용자: "전체 시스템을 마이크로서비스로 마이그레이션해줘 ..."
bkit-rules 자동 적용:
  R5: > 1000 chars + "migrate" 키워드 → Major Feature → Strict
  R2: 현재 monolith → Enterprise 아님
  R7: Agent Teams 제안 (Dynamic+ 검증 필요)
  → Claude는 design 문서 작성을 강제하고 사용자 확인 절차 진행
```

### 시나리오 3: 코드 리뷰 요청 자동 호출

```
사용자: "이 함수 보안 점검해줘"
bkit-rules 자동 적용:
  R3 Task: "security scan" 키워드 → bkit:code-analyzer 자동 호출
  R8: Agent Memory가 이전 세션 컨텍스트 자동 로드
  → code-analyzer가 리뷰 결과 반환
```

[맨 위로](#범례--사용법)

---

## 4. 제약사항

- **user-invocable: false**: 명시 호출 불가. 자동 적용만
- **9 규칙 순차 적용**: 각 규칙이 자체 분기를 포함하지만 1→9 순서는 고정
- **No Guessing 원칙**: 추측 금지. 불확실하면 docs 확인 → 없으면 사용자 질문
- **SoR Priority**: Code > CLAUDE.md > docs/ design 순서로 신뢰
- **Agent Auto-Trigger 거부 조건**: 사용자 명시 거절 / trivial / 프로세스 이해 요청 / 동일 task 이미 호출
- **이모티콘 금지**: 표 마커는 ASCII만 (IMP-021)
- **절대경로 금지**: 모든 경로는 프로젝트 루트 상대경로
- **CLAUDE.md 변경 시 한정**: hot reload로 안 됨. `/clear` 필요
- **Agent Teams 실험 기능**: env var 필수. 미설정 시 제안만 출력
- **계층적 CLAUDE.md**: Area-specific > Project-wide 우선순위

[맨 위로](#범례--사용법)

---

## 5. 갱신 이력

| 날짜 | 변경 | 트리거 |
|------|------|--------|
| 2026-04-11 | Tier-C 신규 생성 (Branching + Linear 9 규칙 + 29 블럭 카드 + 다중 분기 Mermaid) | Option E 세션 1 |

[맨 위로](#범례--사용법)
