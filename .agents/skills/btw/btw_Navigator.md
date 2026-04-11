# btw -- Navigator

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
- 점선 `-.->` = 피드백 루프 (재시도/복귀)
- `:::warning` = 에러/차단/실패 블럭
- `click NODE "#anchor"` = 블럭 상세 카드로 이동

### 스킬 메타

| 항목 | 값 |
|------|-----|
| 이름 | btw |
| Tier | C |
| 커맨드 | `/btw [suggestion]` |
| 프로세스 타입 | Operation Dispatcher (5 ops + 자동 카테고리 감지) |
| 설명 | By-The-Way: 작업 중 개선 제안을 즉시 수집/분류/분석/승격하는 제안 관리자 |

---

## 1. 전체 워크플로우 체계도 {#전체-체계도}

<!-- AUTO:DIAGRAM_MAIN:START -->

```mermaid
%%{init: {"flowchart": {"defaultRenderer": "elk"}, "securityLevel": "loose"} }%%
flowchart TD
    User([사용자 호출]):::io --> Cmd{커맨드 분기}

    Cmd -->|/btw {text}| OpRecord[record<br/>제안 저장]
    Cmd -->|/btw list| OpList[list<br/>전체 출력]
    Cmd -->|/btw analyze| OpAnalyze[analyze<br/>패턴 클러스터링]
    Cmd -->|/btw promote {id}| OpPromote[promote<br/>스킬 승격]
    Cmd -->|/btw stats| OpStats[stats<br/>통계 출력]

    OpRecord --> AutoCat[카테고리 자동 감지]
    AutoCat --> SaveJson[(`.bkit/btw-suggestions.json`)]
    OpList --> ReadJson[JSON 읽기]
    ReadJson --> SaveJson
    OpAnalyze --> Cluster[키워드 클러스터링]
    Cluster --> SkillCand[스킬 후보 도출]
    OpPromote --> Validate{status==pending?}
    Validate -->|예| TriggerCreate[skill-create 트리거]
    Validate -->|아니오| ErrAlready[:::warning 이미 처리됨]:::warning
    OpStats --> CalcStat[통계 계산]
    CalcStat --> Summary[요약 출력]

    SaveJson -.-> ReadJson
    SkillCand -.-> SaveJson
    TriggerCreate --> EndOk([완료]):::io
    Summary --> EndOk

    click User "#node-user-call"
    click Cmd "#node-command-dispatch"
    click OpRecord "#node-op-record"
    click OpList "#node-op-list"
    click OpAnalyze "#node-op-analyze"
    click OpPromote "#node-op-promote"
    click OpStats "#node-op-stats"
    click AutoCat "#node-auto-category"
    click SaveJson "#node-data-file"
    click Cluster "#node-cluster"
    click SkillCand "#node-skill-candidate"
    click Validate "#node-promote-validate"
    click TriggerCreate "#node-trigger-create"
    click ErrAlready "#node-err-already"
    click CalcStat "#node-calc-stat"
    click Summary "#node-summary"

    classDef warning fill:#fee,stroke:#c00,stroke-width:2px
    classDef io fill:#eef,stroke:#338,stroke-width:2px
```

> **패턴**: Operation Dispatcher -- 5개 명시적 커맨드가 중앙 라우터로 분기되며, 모든 op는 단일 데이터 파일(`.bkit/btw-suggestions.json`)을 읽거나 쓴다. record/promote는 외부 시스템(skill-create)으로 연결되는 출구점.

<!-- AUTO:DIAGRAM_MAIN:END -->

<details><summary><strong>블럭 바로가기 (다이어그램 클릭 대안)</strong></summary>

[사용자 호출](#node-user-call) · [커맨드 분기](#node-command-dispatch) · [record](#node-op-record) · [list](#node-op-list) · [analyze](#node-op-analyze) · [promote](#node-op-promote) · [stats](#node-op-stats) · [카테고리 자동 감지](#node-auto-category) · [데이터 파일](#node-data-file) · [키워드 클러스터링](#node-cluster) · [스킬 후보 도출](#node-skill-candidate) · [promote 검증](#node-promote-validate) · [skill-create 트리거](#node-trigger-create) · [이미 처리됨 에러](#node-err-already) · [통계 계산](#node-calc-stat) · [요약 출력](#node-summary)
 · [**전체 블럭 카탈로그**](#block-catalog)

</details>

[맨 위로](#범례--사용법)

---

## 2. 블럭 상세 카탈로그 {#block-catalog}

<details><summary>블럭 카드 펼치기 (16개)</summary>

### 사용자 호출 {#node-user-call}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher 진입점 |
| 동기 | 작업 중 떠오른 개선 아이디어를 컨텍스트 손실 없이 즉시 보존 |
| 내용 | `/btw` 커맨드 5종 중 하나로 호출 (record가 가장 빈도 높음) |
| 동작 방식 | argument-hint `/btw {suggestion} \| /btw list \| /btw analyze \| /btw promote {id} \| /btw stats` |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/btw/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 커맨드 분기 {#node-command-dispatch}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher 중앙 라우터 |
| 동기 | 5개 op를 단일 진입점에서 분기하여 사용자 인터페이스 일관성 유지 |
| 내용 | argument 첫 토큰으로 op 결정 (record는 토큰이 list/analyze/promote/stats가 아닐 때 fallback) |
| 동작 방식 | bash 스크립트 분기 또는 LLM 자체 라우팅 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/btw/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### record op {#node-op-record}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 1/5 (가장 빈도 높음) |
| 동기 | 작업 흐름을 끊지 않고 1초 내에 제안을 저장 |
| 내용 | btw-NNN ID 생성 + ISO timestamp + context(file/pdcaPhase/feature) + status=pending + auto-category |
| 동작 방식 | Read JSON → 다음 ID 계산 → entry 추가 → stats.total++ → Write JSON → 응답 |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### list op {#node-op-list}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 2/5 |
| 동기 | 누적된 제안을 한눈에 검토 + 다음 액션 결정 |
| 내용 | ID/Status/Category/Suggestion(truncated) 4컬럼 표 + 요약 한 줄 |
| 동작 방식 | Read JSON → suggestions 배열 순회 → 표 포맷팅 → 카운트 집계 |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### analyze op {#node-op-analyze}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 3/5 (가장 복잡) |
| 동기 | 누적 제안에서 신규 스킬 후보 또는 기존 스킬 강화 항목 도출 |
| 내용 | pending 제안만 그룹핑 → 키워드 클러스터링 → 스킬 후보 분류(workflow/capability) → 출처 ID 명시 |
| 동작 방식 | Read JSON → category별 그룹 → 키워드 빈도 → workflow vs capability 추정 → analysis 출력 + lastAnalyzed 갱신 |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### promote op {#node-op-promote}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 4/5 (외부 트리거 출구) |
| 동기 | 검증된 제안을 즉시 스킬 생성 파이프라인으로 전달 |
| 내용 | btw-NNN ID로 검색 → status=pending 검증 → status=promoted 갱신 → skill-create 트리거 |
| 동작 방식 | Read JSON → find by id → validate → update → Write JSON → skill-create 호출 안내 |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### stats op {#node-op-stats}

| 항목 | 내용 |
|------|------|
| 소속 | Operation Dispatcher op 5/5 |
| 동기 | 제안 수집/승격 효율 모니터링 + 신규 패턴 트래킹 |
| 내용 | 총합/status별/category별 카운트 + 승격률 + lastAnalyzed + 상위 키워드 |
| 동작 방식 | Read JSON → 다중 집계 → 승격률 계산 → 출력 |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### 카테고리 자동 감지 {#node-auto-category}

| 항목 | 내용 |
|------|------|
| 소속 | record op 후처리 단계 |
| 동기 | 사용자가 카테고리를 명시하지 않아도 자동 분류하여 수집 마찰 최소화 |
| 내용 | 5 카테고리 (skill-request/bug-pattern/improvement/documentation/general) 키워드 매칭 |
| 동작 방식 | suggestion 텍스트 정규식 매칭 우선순위: skill > bug > improvement > documentation > general |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/btw/SKILL.md` (카테고리 매핑 표) |

[다이어그램으로 복귀](#전체-체계도)

### 데이터 파일 {#node-data-file}

| 항목 | 내용 |
|------|------|
| 소속 | 모든 op 공유 영속 저장소 |
| 동기 | 제안/통계의 단일 진실 원천 (single source of truth) |
| 내용 | version/suggestions[]/stats{total/promoted/dismissed/lastAnalyzed} |
| 동작 방식 | 파일 없으면 초기 구조로 생성. 모든 쓰기는 atomic (read → modify → write) |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### 키워드 클러스터링 {#node-cluster}

| 항목 | 내용 |
|------|------|
| 소속 | analyze op 중심 로직 |
| 동기 | 비슷한 제안을 묶어 패턴 발견 (예: @Flow 관련 3개 → 신규 스킬 후보) |
| 내용 | 카테고리 내 키워드 빈도 + 텍스트 유사도 |
| 동작 방식 | 불용어 제거 → 명사 추출 → 빈도 카운트 → 임계값 이상 클러스터 |
| 상태 | [부분] (현재 휴리스틱 기반, 향후 임베딩 가능) |
| 관련 파일 | `.agents/skills/btw/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### 스킬 후보 도출 {#node-skill-candidate}

| 항목 | 내용 |
|------|------|
| 소속 | analyze op 출력 |
| 동기 | 클러스터링 결과를 actionable한 스킬 명세로 변환 |
| 내용 | [NEW SKILL] vs [EXISTING SKILL ENHANCEMENT] + 추정 분류(workflow/capability) + 출처 ID 목록 |
| 동작 방식 | 클러스터 → 스킬명 추론 → 기존 스킬 매칭 → 분류 결정 → 출처 명시 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/btw/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

### promote 검증 {#node-promote-validate}

| 항목 | 내용 |
|------|------|
| 소속 | promote op 가드 |
| 동기 | 이미 promoted/dismissed 된 제안의 중복 처리 방지 |
| 내용 | 대상 제안의 status가 pending인지 확인. 아니면 중단 |
| 동작 방식 | find by ID → if status != pending → throw error |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### skill-create 트리거 {#node-trigger-create}

| 항목 | 내용 |
|------|------|
| 소속 | promote op 외부 출구 |
| 동기 | btw 워크플로우 → 스킬 생성 워크플로우로 자연스럽게 핸드오프 |
| 내용 | suggestion 텍스트를 description seed로, context를 project context로 전달 |
| 동작 방식 | Promoted btw-NNN -> skill-create pipeline. Run /skill-create to continue. 안내 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/skill-create/SKILL.md` (외부 의존) |

[다이어그램으로 복귀](#전체-체계도)

### 이미 처리됨 에러 {#node-err-already}

| 항목 | 내용 |
|------|------|
| 소속 | promote op 차단 분기 |
| 동기 | 사용자에게 명확한 거절 메시지 + 현재 status 안내 |
| 내용 | "btw-NNN is already promoted/dismissed" + 상태 정보 |
| 동작 방식 | error throw → 사용자 출력 |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### 통계 계산 {#node-calc-stat}

| 항목 | 내용 |
|------|------|
| 소속 | stats op 핵심 로직 |
| 동기 | 단순 카운트 + 파생 지표 (승격률, 상위 키워드) 한 번에 계산 |
| 내용 | total / by-status / by-category / promotion-rate / lastAnalyzed / top-keywords |
| 동작 방식 | 단일 패스로 모든 집계 처리 |
| 상태 | [작동] |
| 관련 파일 | `.bkit/btw-suggestions.json` |

[다이어그램으로 복귀](#전체-체계도)

### 요약 출력 {#node-summary}

| 항목 | 내용 |
|------|------|
| 소속 | stats op 출력 단계 |
| 동기 | 사용자에게 한 화면에 핵심 지표 전달 |
| 내용 | 7행 요약 (total/by-status/by-category/promotion-rate/lastAnalyzed/top-keywords) |
| 동작 방식 | 마크다운 코드블럭 포맷팅 |
| 상태 | [작동] |
| 관련 파일 | `.agents/skills/btw/SKILL.md` |

[다이어그램으로 복귀](#전체-체계도)

</details>

[맨 위로](#범례--사용법)

---

## 3. 사용 시나리오

### 시나리오 1: 작업 중 떠오른 스킬 아이디어 즉시 기록

```
사용자: /btw @Flow 모델에서 옵션 목록 자동 검증 필요
btw: Recorded btw-001: @Flow 모델에서 옵션 목록 자동 검증 필요
     category=skill-request, status=pending
```

- record op 실행
- auto-category가 "skill" 키워드 매칭 → skill-request 분류
- 작업 흐름 끊김 없이 1초 내 저장

### 시나리오 2: 누적 제안 분석 → 신규 스킬 후보 도출

```
사용자: /btw analyze
btw: Skill Candidates from /btw Analysis
     ====================================
     1. [NEW SKILL] hunikflow-validation (capability)
        Based on: btw-001, btw-005, btw-008
        Frequency: 3 mentions
        Description: @Flow 엔티티 검증 패턴 가이드
```

- analyze op 실행
- pending 제안 클러스터링
- 3개 이상 유사 제안 → 신규 스킬 후보
- 출처 ID 명시로 추적 가능

### 시나리오 3: 검증된 제안을 스킬로 승격

```
사용자: /btw promote btw-001
btw: Promoted btw-001 -> skill-create pipeline.
     Run /skill-create to continue.
```

- promote op 실행
- status==pending 확인 통과
- btw-001 → status=promoted 갱신
- skill-create 워크플로우로 핸드오프

[맨 위로](#범례--사용법)

---

## 4. 제약사항

- **데이터 손상 방지**: `.bkit/btw-suggestions.json` 직접 편집 금지. 모든 변경은 op를 통해서만
- **promote 1회 제한**: 이미 promoted/dismissed인 제안은 재승격 불가
- **외부 의존**: promote op는 skill-create 스킬 존재를 가정. 없으면 안내만 출력하고 종료
- **이모티콘 금지**: 제안 텍스트 + Navigator 표 마커 모두 ASCII만 (IMP-021)
- **절대경로 금지**: 모든 경로는 프로젝트 루트 상대경로 (PostToolUse 훅 차단)
- **자동 카테고리 한계**: 휴리스틱 기반이므로 오분류 가능. 사용자는 list로 검토 후 필요 시 수동 정정 가능
- **PDCA Context 의존**: `.bkit-memory.json` 없으면 context.pdcaPhase가 null로 저장됨

[맨 위로](#범례--사용법)

---

## 5. 갱신 이력

| 날짜 | 변경 | 트리거 |
|------|------|--------|
| 2026-04-11 | Tier-C 신규 생성 (Operation Dispatcher 5 ops + 16 블럭 카드 + Mermaid) | Option E 세션 1 |

[맨 위로](#범례--사용법)
