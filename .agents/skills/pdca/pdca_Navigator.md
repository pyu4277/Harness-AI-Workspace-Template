# pdca -- Navigator

> SYSTEM_NAVIGATOR 스타일 시각적 네비게이터
> 최종 갱신: 2026-04-11 (Tier-C 신규 생성, Option E 세션 1)
> SKILL.md와 교차 참조 (이 파일은 SKILL.md의 시각화 계층)

---

## 0. 범례 + 사용법 {#범례--사용법}

### 상태 표시

| 표시 | 의미 |
|------|------|
| **[작동]** | 정상 작동 중 |
| **[부분]** | 일부만 작동 (실험 기능 또는 환경변수 의존) |
| **[미구현]** | 설계만 있고 구현 없음 |

### 다이어그램 규약

- ISO 5807:1985 표준 기호 준수
- Mermaid ELK 렌더러 + `securityLevel: loose`
- 점선 `-.->` = 자동 트리거 / 다음 phase 제안
- `:::warning` = 차단/거절/실패 분기
- `click NODE "#anchor"` = 블럭 상세 카드로 이동

### 스킬 메타

| 항목 | 값 |
|------|-----|
| 이름 | pdca |
| Tier | C |
| 커맨드 | `/pdca [action] [feature]` |
| 프로세스 타입 | Operation Dispatcher (12 ops + 4 agent 통합 + Team Mode) |
| 설명 | PDCA 사이클 전체 관리 (PM → Plan → Design → Do → Check → Act → Report → Archive). 12 명령 + Agent Teams 병렬화 |

---

## 1. 전체 워크플로우 체계도 {#전체-체계도}

<!-- AUTO:DIAGRAM_MAIN:START -->

```mermaid
%%{init: {"flowchart": {"defaultRenderer": "elk"}, "securityLevel": "loose"} }%%
flowchart TD
    User([/pdca {action} {feature}]):::io --> Cmd{Action 분기}

    Cmd -->|pm| OpPm[pm<br/>PM Agent Team<br/>4 sub-agents]
    Cmd -->|plan| OpPlan[plan<br/>Plan 문서 생성]
    Cmd -->|design| OpDesign[design<br/>Design 문서]
    Cmd -->|do| OpDo[do<br/>구현 가이드]
    Cmd -->|analyze| OpAnalyze[analyze<br/>gap-detector<br/>Match Rate]
    Cmd -->|iterate| OpIterate[iterate<br/>pdca-iterator<br/>자동 수정]
    Cmd -->|report| OpReport[report<br/>report-generator]
    Cmd -->|team| OpTeam[team<br/>Agent Teams 시작]
    Cmd -->|archive| OpArchive[archive<br/>문서 이동]
    Cmd -->|cleanup| OpCleanup[cleanup<br/>status 정리]
    Cmd -->|status| OpStatus[status<br/>현재 phase 출력]
    Cmd -->|next| OpNext[next<br/>다음 phase 제안]

    OpPm --> PmLead[pm-lead orchestrate<br/>discovery+strategy+research]
    PmLead --> PrdDoc[(`docs/00-pm/{f}.prd.md`)]
    PrdDoc -.->|next phase| OpPlan

    OpPlan --> PrdCheck{PRD 존재?}
    PrdCheck -->|예| ReadPrd[PRD를 컨텍스트로 활용]
    PrdCheck -->|아니오| TipPm[/팁: pm 먼저 실행/]
    ReadPrd --> PlanDoc[(`docs/01-plan/features/{f}.plan.md`)]
    TipPm --> PlanDoc
    PlanDoc -.-> OpDesign

    OpDesign --> CheckPlan{Plan 존재?}
    CheckPlan -->|아니오| ErrNoPlan[:::warning Plan 필요]:::warning
    CheckPlan -->|예| DesignDoc[(`docs/02-design/features/{f}.design.md`)]
    DesignDoc -.-> OpDo

    OpDo --> CheckDesign{Design 존재?}
    CheckDesign -->|아니오| ErrNoDesign[:::warning Design 필요]:::warning
    CheckDesign -->|예| ImplGuide[구현 순서 가이드]
    ImplGuide -.-> OpAnalyze

    OpAnalyze --> GapDetect[gap-detector<br/>Design vs Code 비교]
    GapDetect --> MatchRate{Match Rate}
    MatchRate -->|>= 90%| OpReport
    MatchRate -->|< 90%| OpIterate

    OpIterate --> PdcaIter[pdca-iterator<br/>자동 코드 수정]
    PdcaIter --> ReCheck[자동 재검증]
    ReCheck --> IterCount{count >= 5?}
    IterCount -->|아니오| MatchRate
    IterCount -->|예| StopIter[:::warning 5회 초과 중단]:::warning

    OpReport --> ReportGen[report-generator<br/>4-phase 통합 보고서]
    ReportGen --> RepDoc[(`docs/04-report/{f}.report.md`)]
    RepDoc -.-> OpArchive

    OpArchive --> CheckReport{Report 완료?}
    CheckReport -->|아니오| ErrNoReport[:::warning Report 필요]:::warning
    CheckReport -->|예| MoveDoc[YYYY-MM 폴더로 이동]
    MoveDoc --> ArchiveIdx[(`docs/archive/YYYY-MM/`)]

    OpCleanup --> ArchList[archived feature 목록]
    ArchList --> ConfirmDel[/사용자 확인/]
    ConfirmDel --> DelStatus[(.pdca-status.json 정리)]

    OpStatus --> ReadMem[(`.bkit-memory.json`)]
    ReadMem --> Visualize[phase 시각화]

    OpNext --> CurrentPhase{현재 phase}
    CurrentPhase -->|None| Sugg1[/pdca pm 추천]
    CurrentPhase -->|pm| Sugg2[/pdca plan]
    CurrentPhase -->|plan| Sugg3[/pdca design]
    CurrentPhase -->|design| Sugg4[/pdca do]
    CurrentPhase -->|do| Sugg5[/pdca analyze]
    CurrentPhase -->|check<90%| Sugg6[/pdca iterate]
    CurrentPhase -->|check>=90%| Sugg7[/pdca report]
    CurrentPhase -->|report| Sugg8[/pdca archive]

    OpTeam --> TeamCheck{Agent Teams<br/>enabled?}
    TeamCheck -->|아니오| ErrNoTeam[:::warning env 미설정]:::warning
    TeamCheck -->|예| LevelDetect[Level 감지]
    LevelDetect -->|Starter| ErrNotSupport[:::warning Starter 미지원]:::warning
    LevelDetect -->|Dynamic 3| Strategy3[3 teammates<br/>dev+frontend+qa]
    LevelDetect -->|Enterprise 5| Strategy5[5 teammates<br/>+architect+reviewer+security]
    Strategy3 --> CtoLead[cto-lead orchestrate]
    Strategy5 --> CtoLead
    CtoLead --> AssignTask[teammate 할당]

    classDef warning fill:#fee,stroke:#c00,stroke-width:2px
    classDef io fill:#eef,stroke:#338,stroke-width:2px

    click User "#node-user-call"
    click Cmd "#node-action-dispatch"
    click OpPm "#node-op-pm"
    click OpPlan "#node-op-plan"
    click OpDesign "#node-op-design"
    click OpDo "#node-op-do"
    click OpAnalyze "#node-op-analyze"
    click OpIterate "#node-op-iterate"
    click OpReport "#node-op-report"
    click OpTeam "#node-op-team"
    click OpArchive "#node-op-archive"
    click OpCleanup "#node-op-cleanup"
    click OpStatus "#node-op-status"
    click OpNext "#node-op-next"
    click PmLead "#node-pm-lead"
    click PrdDoc "#node-prd-doc"
    click PrdCheck "#node-prd-check"
    click ReadPrd "#node-read-prd"
    click TipPm "#node-tip-pm"
    click PlanDoc "#node-plan-doc"
    click CheckPlan "#node-check-plan"
    click ErrNoPlan "#node-err-no-plan"
    click DesignDoc "#node-design-doc"
    click CheckDesign "#node-check-design"
    click ErrNoDesign "#node-err-no-design"
    click ImplGuide "#node-impl-guide"
    click GapDetect "#node-gap-detect"
    click MatchRate "#node-match-rate"
    click PdcaIter "#node-pdca-iter"
    click ReCheck "#node-re-check"
    click IterCount "#node-iter-count"
    click StopIter "#node-stop-iter"
    click ReportGen "#node-report-gen"
    click RepDoc "#node-report-doc"
    click CheckReport "#node-check-report"
    click ErrNoReport "#node-err-no-report"
    click MoveDoc "#node-move-doc"
    click ArchiveIdx "#node-archive-idx"
    click ArchList "#node-arch-list"
    click ConfirmDel "#node-confirm-del"
    click DelStatus "#node-del-status"
    click ReadMem "#node-read-mem"
    click Visualize "#node-visualize"
    click TeamCheck "#node-team-check"
    click ErrNoTeam "#node-err-no-team"
    click LevelDetect "#node-level-detect"
    click ErrNotSupport "#node-err-not-support"
    click Strategy3 "#node-strategy-3"
    click Strategy5 "#node-strategy-5"
    click CtoLead "#node-cto-lead"
    click AssignTask "#node-assign-task"
```

> **패턴**: Operation Dispatcher -- 12개 명시적 ops가 중앙 라우터로 분기. 4 agent 통합 (pm-lead/gap-detector/pdca-iterator/report-generator). pm → plan → design → do → analyze → (iterate ↔ analyze 루프) → report → archive의 표준 PDCA 사이클이 op 간 자동 제안으로 연결. Team Mode는 Dynamic/Enterprise에서 병렬화 옵션.

<!-- AUTO:DIAGRAM_MAIN:END -->

<details><summary><strong>블럭 바로가기 (다이어그램 클릭 대안)</strong></summary>

[사용자 호출](#node-user-call) · [Action 분기](#node-action-dispatch) · [pm op](#node-op-pm) · [pm-lead](#node-pm-lead) · [PRD 문서](#node-prd-doc) · [plan op](#node-op-plan) · [PRD 체크](#node-prd-check) · [PRD 활용](#node-read-prd) · [pm 팁](#node-tip-pm) · [Plan 문서](#node-plan-doc) · [design op](#node-op-design) · [Plan 체크](#node-check-plan) · [Plan 부재 에러](#node-err-no-plan) · [Design 문서](#node-design-doc) · [do op](#node-op-do) · [Design 체크](#node-check-design) · [Design 부재 에러](#node-err-no-design) · [구현 가이드](#node-impl-guide) · [analyze op](#node-op-analyze) · [gap-detector](#node-gap-detect) · [Match Rate 분기](#node-match-rate) · [iterate op](#node-op-iterate) · [pdca-iterator](#node-pdca-iter) · [재검증](#node-re-check) · [반복 횟수 분기](#node-iter-count) · [5회 초과 중단](#node-stop-iter) · [report op](#node-op-report) · [report-generator](#node-report-gen) · [Report 문서](#node-report-doc) · [archive op](#node-op-archive) · [Report 체크](#node-check-report) · [Report 부재 에러](#node-err-no-report) · [문서 이동](#node-move-doc) · [Archive 폴더](#node-archive-idx) · [cleanup op](#node-op-cleanup) · [archive 목록](#node-arch-list) · [사용자 확인](#node-confirm-del) · [status 정리](#node-del-status) · [status op](#node-op-status) · [bkit-memory 읽기](#node-read-mem) · [phase 시각화](#node-visualize) · [next op](#node-op-next) · [team op](#node-op-team) · [Agent Teams 체크](#node-team-check) · [Team env 미설정 에러](#node-err-no-team) · [Level 감지](#node-level-detect) · [Starter 미지원 에러](#node-err-not-support) · [Dynamic 3](#node-strategy-3) · [Enterprise 5](#node-strategy-5) · [cto-lead](#node-cto-lead) · [teammate 할당](#node-assign-task)
 · [**전체 블럭 카탈로그**](#block-catalog)

</details>

[맨 위로](#범례--사용법)

---

## 2. 블럭 상세 카탈로그 {#block-catalog}

<details><summary>블럭 카드 펼치기 (50개)</summary>

### 사용자 호출 {#node-user-call}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher 진입점 |
| 동기 | PDCA 사이클을 단일 커맨드로 통합 관리 (12 ops) |
| 내용 | `/pdca [action] [feature]` 형식. action 12종 + feature 이름 |
| 동작 방식 | argument-hint `[action] [feature]`. argument로 op 분기 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Action 분기 {#node-action-dispatch}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher 중앙 라우터 |
| 동기 | 12개 op를 단일 진입점에서 분기 |
| 내용 | pm/plan/design/do/analyze/iterate/report/team/archive/cleanup/status/next |
| 동작 방식 | LLM이 첫 토큰을 op로 매핑. legacy /pdca-* 명령도 자동 변환 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### pm op {#node-op-pm}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 1/12 (Pre-Plan) |
| 동기 | Plan 전 PM Agent Team이 비즈니스 문맥 + 시장 분석 사전 수행 |
| 내용 | pm-lead 호출 → 4 sub-agent (discovery/strategy/research/prd) 순차 실행 → PRD 생성 |
| 동작 방식 | Phase 1 Context → Phase 2 Parallel (3 agents) → Phase 3 PRD Synthesis |
| 상태 | [부분] (Agent Teams env 필요, Dynamic+ only) |
| 관련 파일 | `docs/00-pm/{feature}.prd.md` |

[다이어그램으로 복귀](#전체-체계도)

### pm-lead orchestrate {#node-pm-lead}

| 항목 | 내용 |
|------|------|
| 소속 | pm op 핵심 agent |
| 동기 | 4 sub-agent를 단일 lead가 조율하여 PRD 합성 |
| 내용 | pm-discovery (Opportunity Solution Tree, Teresa Torres) + pm-strategy (JTBD + Lean Canvas) + pm-research (3 personas + 5 competitors + TAM/SAM/SOM) + pm-prd (Beachhead + GTM + 8-section PRD) |
| 동작 방식 | Phase 1-3 순차. Phase 2는 3 agent 병렬 |
| 상태 | [부분] |
| 관련 파일 | `.claude/agents/bkit/pm-lead.md` |

[다이어그램으로 복귀](#전체-체계도)

### PRD 문서 {#node-prd-doc}

| 항목 | 내용 |
|------|------|
| 소속 | pm op 출력 |
| 동기 | Plan 단계의 입력 컨텍스트로 활용 |
| 내용 | Beachhead Segment + GTM Strategy + 8-section PRD |
| 동작 방식 | Write to `docs/00-pm/{feature}.prd.md` + Task `[PM] {feature}` 생성 + .bkit-memory.json phase=pm |
| 상태 | [부분] |
| 관련 파일 | `docs/00-pm/{feature}.prd.md` |

[다이어그램으로 복귀](#전체-체계도)

### plan op {#node-op-plan}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 2/12 (Plan Phase) |
| 동기 | 기능 기획 문서 생성 (PDCA P 단계) |
| 내용 | PRD auto-reference + plan.template.md + Executive Summary 4-perspective |
| 동작 방식 | docs/00-pm/{f}.prd.md 확인 → Read PRD → Plan 생성 → Executive Summary 응답 출력 (MANDATORY) |
| 상태 | [작동] |
| 관련 파일 | `docs/01-plan/features/{feature}.plan.md` |

[다이어그램으로 복귀](#전체-체계도)

### PRD 체크 {#node-prd-check}

| 항목 | 내용 |
|------|------|
| 소속 | plan op 분기 결정 |
| 동기 | PRD가 있으면 Plan 품질 향상, 없어도 진행 가능 |
| 내용 | docs/00-pm/{f}.prd.md 존재 확인 |
| 동작 방식 | Read 시도 → 성공 시 활용, 실패 시 팁 출력 |
| 상태 | [작동] |
| 관련 파일 | `docs/00-pm/` |

[다이어그램으로 복귀](#전체-체계도)

### PRD 활용 {#node-read-prd}

| 항목 | 내용 |
|------|------|
| 소속 | plan op → PRD 발견 분기 |
| 동기 | PM 단계 결과를 자동 재사용으로 품질 향상 |
| 내용 | PRD를 컨텍스트로 Plan 생성 |
| 동작 방식 | Read PRD → LLM 컨텍스트 주입 → Plan 작성 |
| 상태 | [작동] |
| 관련 파일 | `docs/00-pm/{feature}.prd.md` |

[다이어그램으로 복귀](#전체-체계도)

### pm 팁 {#node-tip-pm}

| 항목 | 내용 |
|------|------|
| 소속 | plan op → PRD 부재 분기 |
| 동기 | PM 없어도 진행하지만 더 좋은 결과 유도 |
| 내용 | "tip: run /pdca pm {feature} first for better results" |
| 동작 방식 | 텍스트 안내. Plan은 그대로 진행 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Plan 문서 {#node-plan-doc}

| 항목 | 내용 |
|------|------|
| 소속 | plan op 출력 |
| 동기 | 기능 기획의 단일 진실 원천 |
| 내용 | plan.template.md 구조 + Executive Summary 4-perspective (Problem/Solution/Function UX Effect/Core Value) |
| 동작 방식 | Write + Task `[Plan] {feature}` + .bkit-memory.json phase=plan + Executive Summary 응답 출력 |
| 상태 | [작동] |
| 관련 파일 | `docs/01-plan/features/{feature}.plan.md` |

[다이어그램으로 복귀](#전체-체계도)

### design op {#node-op-design}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 3/12 (Design Phase) |
| 동기 | 구현 전 상세 설계 (PDCA P 단계) |
| 내용 | Plan 검증 + design.template.md 기반 생성 |
| 동작 방식 | Plan 존재 확인 → design 작성 → Task blockedBy Plan |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/features/{feature}.design.md` |

[다이어그램으로 복귀](#전체-체계도)

### Plan 체크 {#node-check-plan}

| 항목 | 내용 |
|------|------|
| 소속 | design op 가드 |
| 동기 | Plan 없이 design 진행 차단 |
| 내용 | docs/01-plan/features/{f}.plan.md 존재 확인 |
| 동작 방식 | Read 시도 → 실패 시 ErrNoPlan |
| 상태 | [작동] |
| 관련 파일 | `docs/01-plan/features/` |

[다이어그램으로 복귀](#전체-체계도)

### Plan 부재 에러 {#node-err-no-plan}

| 항목 | 내용 |
|------|------|
| 소속 | design op 차단 분기 |
| 동기 | Plan 없으면 design 진행 불가 |
| 내용 | "Plan document required. Run /pdca plan {feature} first" |
| 동작 방식 | error throw + 가이드 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Design 문서 {#node-design-doc}

| 항목 | 내용 |
|------|------|
| 소속 | design op 출력 |
| 동기 | 상세 구현 방향 명시 |
| 내용 | design.template.md 구조 + Plan 참조 |
| 동작 방식 | Write + Task `[Design] {feature}` (blockedBy: Plan) + .bkit-memory.json phase=design |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/features/{feature}.design.md` |

[다이어그램으로 복귀](#전체-체계도)

### do op {#node-op-do}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 4/12 (Do Phase) |
| 동기 | 실제 구현 시작 (PDCA D 단계) |
| 내용 | Design 검증 + do.template.md 기반 구현 가이드 |
| 동작 방식 | Design 존재 확인 → 구현 순서/파일/의존성 가이드 출력 |
| 상태 | [작동] |
| 관련 파일 | `.agents/templates/do.template.md` |

[다이어그램으로 복귀](#전체-체계도)

### Design 체크 {#node-check-design}

| 항목 | 내용 |
|------|------|
| 소속 | do op 가드 |
| 동기 | Design 없이 do 진행 차단 |
| 내용 | docs/02-design/features/{f}.design.md 존재 확인 |
| 동작 방식 | Read 시도 → 실패 시 ErrNoDesign |
| 상태 | [작동] |
| 관련 파일 | `docs/02-design/features/` |

[다이어그램으로 복귀](#전체-체계도)

### Design 부재 에러 {#node-err-no-design}

| 항목 | 내용 |
|------|------|
| 소속 | do op 차단 분기 |
| 동기 | Design 없으면 구현 방향 불명 |
| 내용 | "Design document required. Run /pdca design {feature} first" |
| 동작 방식 | error throw + 가이드 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 구현 가이드 {#node-impl-guide}

| 항목 | 내용 |
|------|------|
| 소속 | do op 출력 |
| 동기 | 구현 시작점 안내 |
| 내용 | 구현 순서 체크리스트 + 핵심 파일/컴포넌트 + 의존성 설치 명령 |
| 동작 방식 | Design 문서에서 구현 순서 추출 + Task `[Do] {feature}` (blockedBy: Design) |
| 상태 | [작동] |
| 관련 파일 | `.agents/templates/do.template.md` |

[다이어그램으로 복귀](#전체-체계도)

### analyze op {#node-op-analyze}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 5/12 (Check Phase) |
| 동기 | 구현 vs Design 차이 자동 분석 (PDCA C 단계) |
| 내용 | gap-detector agent 호출 + Match Rate 계산 + Gap 목록 |
| 동작 방식 | Do 완료 확인 → gap-detector 호출 → 결과 저장 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/gap-detector.md` |

[다이어그램으로 복귀](#전체-체계도)

### gap-detector {#node-gap-detect}

| 항목 | 내용 |
|------|------|
| 소속 | analyze op 핵심 agent |
| 동기 | Design 문서 vs 구현 코드의 정량 비교 |
| 내용 | Match Rate (%) + Gap list (missing/extra/changed) |
| 동작 방식 | Read Design + Glob 코드 + LLM 비교 → 분석 보고서 |
| 상태 | [작동] |
| 관련 파일 | `docs/03-analysis/{feature}.analysis.md` |

[다이어그램으로 복귀](#전체-체계도)

### Match Rate 분기 {#node-match-rate}

| 항목 | 내용 |
|------|------|
| 소속 | analyze op 결과 분기 |
| 동기 | 90% 임계값 기준으로 다음 phase 결정 |
| 내용 | >= 90% → report op, < 90% → iterate op |
| 동작 방식 | matchRate 비교 → 자동 제안 |
| 상태 | [작동] |
| 관련 파일 | `.bkit-memory.json` (matchRate 저장) |

[다이어그램으로 복귀](#전체-체계도)

### iterate op {#node-op-iterate}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 6/12 (Act Phase) |
| 동기 | Gap 자동 수정 + 재검증으로 90% 도달 (PDCA A 단계) |
| 내용 | pdca-iterator agent 호출 + 자동 재검증 루프 |
| 동작 방식 | matchRate < 90% 트리거 → iterator → re-analyze → 반복 |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/pdca-iterator.md` |

[다이어그램으로 복귀](#전체-체계도)

### pdca-iterator {#node-pdca-iter}

| 항목 | 내용 |
|------|------|
| 소속 | iterate op 핵심 agent |
| 동기 | Gap list 기반 자동 코드 수정 |
| 내용 | Gap 항목별 수정 패치 적용 |
| 동작 방식 | Read Gap → Edit/Write 코드 → Task `[Act-N] {feature}` (N=count) |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/pdca-iterator.md` |

[다이어그램으로 복귀](#전체-체계도)

### 재검증 {#node-re-check}

| 항목 | 내용 |
|------|------|
| 소속 | iterate op 후처리 |
| 동기 | 수정 후 즉시 재검증으로 효과 확인 |
| 내용 | analyze op 자동 재실행 |
| 동작 방식 | gap-detector 재호출 → matchRate 재계산 |
| 상태 | [작동] |
| 관련 파일 | `docs/03-analysis/{feature}.analysis.md` |

[다이어그램으로 복귀](#전체-체계도)

### 반복 횟수 분기 {#node-iter-count}

| 항목 | 내용 |
|------|------|
| 소속 | iterate op 종료 조건 |
| 동기 | 무한 루프 방지 (5회 한도) |
| 내용 | iteration count >= 5 또는 matchRate >= 90% 시 종료 |
| 동작 방식 | bkit.config.json maxIterations 참조 |
| 상태 | [작동] |
| 관련 파일 | `bkit.config.json` |

[다이어그램으로 복귀](#전체-체계도)

### 5회 초과 중단 {#node-stop-iter}

| 항목 | 내용 |
|------|------|
| 소속 | iterate op 차단 분기 |
| 동기 | 5회 시도 후에도 90% 미달 시 사용자 개입 필요 |
| 내용 | "Max iterations reached. Manual review required" |
| 동작 방식 | 종료 + 마지막 Gap 보고서 출력 |
| 상태 | [작동] |
| 관련 파일 | `.bkit-memory.json` |

[다이어그램으로 복귀](#전체-체계도)

### report op {#node-op-report}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 7/12 (Completion) |
| 동기 | 4-phase 통합 보고서 생성 |
| 내용 | report-generator agent + Executive Summary 1.3 Value Delivered 4-perspective |
| 동작 방식 | matchRate >= 90% 검증 → report-generator → Write report → Executive Summary 응답 출력 (MANDATORY) |
| 상태 | [작동] |
| 관련 파일 | `docs/04-report/{feature}.report.md` |

[다이어그램으로 복귀](#전체-체계도)

### report-generator {#node-report-gen}

| 항목 | 내용 |
|------|------|
| 소속 | report op 핵심 agent |
| 동기 | Plan/Design/Implementation/Analysis 통합 |
| 내용 | report.template.md 기반 + 메트릭 + 4 perspective Value |
| 동작 방식 | 4 phase 문서 + 코드 + analysis 통합 → Write |
| 상태 | [작동] |
| 관련 파일 | `.claude/agents/bkit/report-generator.md` |

[다이어그램으로 복귀](#전체-체계도)

### Report 문서 {#node-report-doc}

| 항목 | 내용 |
|------|------|
| 소속 | report op 출력 |
| 동기 | 외부 공유 가능한 완료 보고서 |
| 내용 | Plan/Design/Implementation/Analysis 통합 + Executive Summary |
| 동작 방식 | Write + Task `[Report] {feature}` + .bkit-memory.json phase=completed |
| 상태 | [작동] |
| 관련 파일 | `docs/04-report/{feature}.report.md` |

[다이어그램으로 복귀](#전체-체계도)

### archive op {#node-op-archive}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 8/12 (Cleanup) |
| 동기 | 완료된 PDCA 문서 보존 + 활성 폴더 정리 |
| 내용 | Report 검증 + YYYY-MM 폴더로 이동 + Archive Index 갱신 |
| 동작 방식 | matchRate >= 90% 또는 phase=completed 검증 → 4 문서 이동 → _INDEX.md 갱신 |
| 상태 | [작동] |
| 관련 파일 | `docs/archive/YYYY-MM/{feature}/` |

[다이어그램으로 복귀](#전체-체계도)

### Report 체크 {#node-check-report}

| 항목 | 내용 |
|------|------|
| 소속 | archive op 가드 |
| 동기 | Report 없이 archive 진행 차단 |
| 내용 | phase=completed 또는 matchRate >= 90% 확인 |
| 동작 방식 | .bkit-memory.json 또는 .pdca-status.json 읽기 |
| 상태 | [작동] |
| 관련 파일 | `.bkit-memory.json` |

[다이어그램으로 복귀](#전체-체계도)

### Report 부재 에러 {#node-err-no-report}

| 항목 | 내용 |
|------|------|
| 소속 | archive op 차단 분기 |
| 동기 | 미완료 PDCA 사이클 보존 차단 |
| 내용 | "Cannot archive before Report completion" |
| 동작 방식 | error throw + 현재 phase 안내 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 문서 이동 {#node-move-doc}

| 항목 | 내용 |
|------|------|
| 소속 | archive op 핵심 동작 |
| 동기 | 4 문서를 단일 폴더로 통합 + 원본 삭제 |
| 내용 | plan/design/analysis/report 4 파일 이동 |
| 동작 방식 | Read → Write → 원본 삭제 (irreversible). --summary 옵션 시 status에 70% 축약 보존 |
| 상태 | [작동] |
| 관련 파일 | `docs/archive/YYYY-MM/{feature}/` |

[다이어그램으로 복귀](#전체-체계도)

### Archive 폴더 {#node-archive-idx}

| 항목 | 내용 |
|------|------|
| 소속 | archive op 출력 |
| 동기 | 월별 archive 인덱스 자동 갱신 |
| 내용 | docs/archive/YYYY-MM/_INDEX.md 자동 갱신 |
| 동작 방식 | Append archive entry → .pdca-status.json archivedTo 갱신 |
| 상태 | [작동] |
| 관련 파일 | `docs/archive/YYYY-MM/_INDEX.md` |

[다이어그램으로 복귀](#전체-체계도)

### cleanup op {#node-op-cleanup}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 9/12 (v1.4.8) |
| 동기 | .pdca-status.json 크기 축소 (archived feature 정리) |
| 내용 | archived feature 목록 + 사용자 확인 + 삭제 |
| 동작 방식 | getArchivedFeatures() → AskUserQuestion → cleanupArchivedFeatures() |
| 상태 | [작동] |
| 관련 파일 | `lib/pdca/status.js` |

[다이어그램으로 복귀](#전체-체계도)

### archive 목록 {#node-arch-list}

| 항목 | 내용 |
|------|------|
| 소속 | cleanup op 입력 |
| 동기 | 사용자에게 정리 대상 표시 |
| 내용 | archived feature + timestamps + archive paths |
| 동작 방식 | .pdca-status.json 읽기 → 필터 archived |
| 상태 | [작동] |
| 관련 파일 | `.pdca-status.json` |

[다이어그램으로 복귀](#전체-체계도)

### 사용자 확인 {#node-confirm-del}

| 항목 | 내용 |
|------|------|
| 소속 | cleanup op 가드 |
| 동기 | 실수로 활성 feature 삭제 방지 |
| 내용 | AskUserQuestion: "Select features to cleanup" |
| 동작 방식 | multiSelect 또는 'all' 옵션 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### status 정리 {#node-del-status}

| 항목 | 내용 |
|------|------|
| 소속 | cleanup op 출력 |
| 동기 | .pdca-status.json만 정리 (archive 문서는 보존) |
| 내용 | deleteFeatureFromStatus(feature) |
| 동작 방식 | JSON 수정 후 atomic write |
| 상태 | [작동] |
| 관련 파일 | `.pdca-status.json` |

[다이어그램으로 복귀](#전체-체계도)

### status op {#node-op-status}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 10/12 (조회) |
| 동기 | 현재 PDCA 상태 시각화 |
| 내용 | feature/phase/Match Rate/Iteration count + 진행 시각화 |
| 동작 방식 | Read .bkit-memory.json → 표 출력 |
| 상태 | [작동] |
| 관련 파일 | `.bkit-memory.json` |

[다이어그램으로 복귀](#전체-체계도)

### bkit-memory 읽기 {#node-read-mem}

| 항목 | 내용 |
|------|------|
| 소속 | status op 입력 |
| 동기 | 단일 진실 원천에서 상태 로드 |
| 내용 | feature/phase/matchRate/iteration |
| 동작 방식 | Read JSON |
| 상태 | [작동] |
| 관련 파일 | `.bkit-memory.json` |

[다이어그램으로 복귀](#전체-체계도)

### phase 시각화 {#node-visualize}

| 항목 | 내용 |
|------|------|
| 소속 | status op 출력 |
| 동기 | 5 phase 진행을 한 줄로 표시 |
| 내용 | [Plan] -> [Design] -> [Do] -> [Check] -> [Act] 마커 |
| 동작 방식 | 현재 phase 강조 + 완료 phase ASCII 마크 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### next op {#node-op-next}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 11/12 (안내) |
| 동기 | 현재 phase에서 다음 액션 자동 제안 |
| 내용 | 8 phase 매핑 표 (None → pm → plan → design → do → check → act/report → archive) |
| 동작 방식 | 현재 phase 읽기 → AskUserQuestion으로 다음 명령 확인 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### team op {#node-op-team}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 12/12 (v1.5.1, 병렬화) |
| 동기 | Dynamic/Enterprise 프로젝트에서 PDCA 병렬 가속 |
| 내용 | team [feature] / team status / team cleanup 3 sub-ops |
| 동작 방식 | env 검증 → Level 감지 → strategy 생성 → cto-lead 시작 |
| 상태 | [부분] (실험 기능, env 필요) |
| 관련 파일 | `lib/team/coordinator.js` |

[다이어그램으로 복귀](#전체-체계도)

### Agent Teams 체크 {#node-team-check}

| 항목 | 내용 |
|------|------|
| 소속 | team op 가드 |
| 동기 | env 미설정 시 즉시 차단 |
| 내용 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 확인 |
| 동작 방식 | isTeamModeAvailable() 호출 |
| 상태 | [부분] |
| 관련 파일 | `lib/team/coordinator.js` |

[다이어그램으로 복귀](#전체-체계도)

### Team env 미설정 에러 {#node-err-no-team}

| 항목 | 내용 |
|------|------|
| 소속 | team op 차단 분기 |
| 동기 | env 미설정 시 명확한 안내 |
| 내용 | "Agent Teams is not enabled. Set CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1" |
| 동작 방식 | error 출력 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Level 감지 {#node-level-detect}

| 항목 | 내용 |
|------|------|
| 소속 | team op 분기 결정 |
| 동기 | Level별 다른 teammate 구성 |
| 내용 | detectLevel() 호출. Starter 미지원, Dynamic 3, Enterprise 5 |
| 동작 방식 | bkit-rules R2 (Level Auto-Detection) 재사용 |
| 상태 | [작동] |
| 관련 파일 | `lib/level/detector.js` |

[다이어그램으로 복귀](#전체-체계도)

### Starter 미지원 에러 {#node-err-not-support}

| 항목 | 내용 |
|------|------|
| 소속 | team op 차단 분기 |
| 동기 | Starter 프로젝트는 단일 세션 PDCA로 충분 |
| 내용 | "Starter projects cannot use Team Mode" |
| 동작 방식 | error 출력 + 일반 PDCA 안내 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/pdca/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### Dynamic 3 strategy {#node-strategy-3}

| 항목 | 내용 |
|------|------|
| 소속 | team op → Dynamic 분기 |
| 동기 | 백엔드/풀스택에 적합한 3 teammate 구성 |
| 내용 | developer + frontend + qa |
| 동작 방식 | generateTeamStrategy('dynamic') |
| 상태 | [부분] |
| 관련 파일 | `lib/team/coordinator.js` |

[다이어그램으로 복귀](#전체-체계도)

### Enterprise 5 strategy {#node-strategy-5}

| 항목 | 내용 |
|------|------|
| 소속 | team op → Enterprise 분기 |
| 동기 | 마이크로서비스/대규모에 적합한 5 teammate |
| 내용 | architect + developer + qa + reviewer + security |
| 동작 방식 | generateTeamStrategy('enterprise') |
| 상태 | [부분] |
| 관련 파일 | `lib/team/coordinator.js` |

[다이어그램으로 복귀](#전체-체계도)

### cto-lead orchestrate {#node-cto-lead}

| 항목 | 내용 |
|------|------|
| 소속 | team op 핵심 agent (opus) |
| 동기 | 기술 방향 + 작업 분배 + 품질 게이트 |
| 내용 | cto-lead agent가 PDCA phase별 패턴 선택 (leader/swarm/council/watchdog) |
| 동작 방식 | Phase별 전략: Dynamic={leader/leader/swarm/council/leader}, Enterprise={leader/council/swarm/council/watchdog} |
| 상태 | [부분] |
| 관련 파일 | `.claude/agents/bkit/cto-lead.md` |

[다이어그램으로 복귀](#전체-체계도)

### teammate 할당 {#node-assign-task}

| 항목 | 내용 |
|------|------|
| 소속 | team op 출력 |
| 동기 | PDCA phase별로 적합한 teammate에게 작업 분배 |
| 내용 | assignNextTeammateWork() |
| 동작 방식 | 90% Match Rate threshold 강제 + 현재 phase 기반 분배 |
| 상태 | [부분] |
| 관련 파일 | `lib/team/coordinator.js` |

[다이어그램으로 복귀](#전체-체계도)

</details>

[맨 위로](#범례--사용법)

---

## 3. 사용 시나리오

### 시나리오 1: 표준 PDCA 사이클 완주

```
사용자: /pdca pm user-authentication
pdca: PM Agent Team 4 sub-agents 실행 → docs/00-pm/user-authentication.prd.md 생성

사용자: /pdca plan user-authentication
pdca: PRD 발견 → 컨텍스트 활용 → docs/01-plan/features/user-authentication.plan.md 생성
       Executive Summary 응답에 출력

사용자: /pdca design user-authentication
pdca: Plan 검증 → docs/02-design/features/user-authentication.design.md 생성

사용자: /pdca do user-authentication
pdca: Design 검증 → 구현 가이드 출력 (사용자가 실제 구현)

사용자: /pdca analyze user-authentication
pdca: gap-detector → Match Rate 75% → /pdca iterate 자동 제안

사용자: /pdca iterate user-authentication
pdca: pdca-iterator → 자동 수정 → 재검증 88% → 1회 더
       2회 후 91% → /pdca report 자동 제안

사용자: /pdca report user-authentication
pdca: report-generator → docs/04-report/user-authentication.report.md
       Executive Summary Value Delivered 응답 출력

사용자: /pdca archive user-authentication
pdca: 4 문서 → docs/archive/2026-04/user-authentication/ 이동
```

### 시나리오 2: 빠른 status 조회 + next 안내

```
사용자: /pdca status
pdca: PDCA Status
     Feature: user-authentication
     Phase: Check (Gap Analysis)
     Match Rate: 85%
     Iteration: 2/5
     [Plan] OK -> [Design] OK -> [Do] OK -> [Check] 진행 -> [Act] 대기

사용자: /pdca next
pdca: 현재 Check 단계 + matchRate < 90%
     다음 단계: /pdca iterate user-authentication 권장
```

### 시나리오 3: Team Mode 병렬 가속 (Enterprise)

```
사용자: /pdca team user-authentication
pdca: Agent Teams 활성 확인 → Enterprise Level 감지
     5 teammates 생성 (architect/developer/qa/reviewer/security)
     cto-lead가 Plan phase에서 leader 패턴 선택
     사용자 확인 후 시작

사용자: /pdca team status
pdca: Team Status
     Agent Teams: Available
     Display Mode: in-process
     Teammates: 5 / 5 (Enterprise)
     Feature: user-authentication
       architect: [Design] in progress
       developer: [Do] waiting
       qa: idle
       reviewer: idle
       security: idle
```

[맨 위로](#범례--사용법)

---

## 4. 제약사항

- **순차 의존성**: design은 Plan, do는 Design, analyze는 Do, report는 Match Rate >= 90% 필요
- **archive 비가역성**: 원본 문서 삭제. 실수 시 git에서 복원
- **iterate 5회 한도**: maxIterations 도달 시 수동 개입 필요
- **PM op는 Dynamic+ only**: Starter 프로젝트는 직접 plan으로 시작
- **Team Mode env 필수**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 미설정 시 차단
- **이모티콘 금지**: 표 마커는 ASCII만 (IMP-021)
- **절대경로 금지**: 모든 경로는 프로젝트 루트 상대경로
- **Hot reload (CC 2.1.0+)**: SKILL.md 변경은 즉시 반영. CLAUDE.md는 /clear 필요
- **bkit-pdca-guide output style 권장**: phase badges + checklists + gap suggestions
- **Domain Integration (004_AI_Project)**: phase별 도메인 스킬 자동 제안 (PaperResearch/HWPX_Master/DocKit/Mermaid_FlowChart 등)
- **Stop hook 통합**: pdca-skill-stop.js (10초 timeout)가 세션 종료 시 자동 검증

[맨 위로](#범례--사용법)

---

## 5. 갱신 이력

| 날짜 | 변경 | 트리거 |
|------|------|--------|
| 2026-04-11 | Tier-C 신규 생성 (Operation Dispatcher 12 ops + 4 agents + 50 블럭 카드 + 대형 Mermaid) | Option E 세션 1 |

[맨 위로](#범례--사용법)
