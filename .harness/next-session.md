# Next Session Entry Point

> 이 파일은 다음 세션 시작 시 **첫 번째로 읽어야 할 파일**입니다.
> 이전 세션 종료 시점, 현재 상태, 다음 작업 선택지를 제공합니다.

## 이전 세션 정보 (2026-04-11 Wiki 진화 3차 -- 100_AI 세션 2-4 자율 진행)

- **세션 시작**: 2026-04-11 (Wiki 진화 2차 직후, 사용자 "나머지 알아서" 지시)
- **세션 종료**: 2026-04-11 (100_AI 세션 2/3/4 연속 완료)

## 이번 작업 (Wiki 진화 3차) 성과

100_AI 대화 저장의 5+ 세션 점진 위키화 계획 중 **세션 2-4 자율 진행**.

### 세션 2: 평가 에이전트 + GravityESS

| entity | 출처 | 핵심 발견 |
|--------|------|----------|
| **Evaluation_Skill_Genesis.md** | 260226 평가 에이전트 89KB | /CIPP평가 → /Evaluation 진화. **Plan A/B 패턴** + **조건부 OCR** + **동적 템플릿 변환 선행** |
| **GravityESS_Project.md** | 260308_GravityESS 51KB | **003_AI_Project 활성 스킬 8 + MCP 4 카탈로그** + RAG 7요소 + Total_SystemRun 4단계 거버넌스 |

### 세션 3: 도구 가이드 5종 통합

| entity | 출처 | 핵심 발견 |
|--------|------|----------|
| **Tool_Guides_Collection_260411.md** | Bkit + Playwright e2e + Notion+Cal + Google Opal + 폴더 메타 | **10-Agent 멀티 오케스트레이션 패턴** (project-orchestrator + 9 sub-agent), **일정 추출 JSON GPT 프롬프트** (Make 호환), **bkit 트리거 키워드 자동 활성** |

### 세션 4: 홈서버 통합

| entity | 출처 | 핵심 발견 |
|--------|------|----------|
| **Smartphone_Home_Server.md** | Phon 87KB + 잠자는 폰 39KB + 영상 2KB | **5단계 아키텍처**: PC → SSH → Termux → Ubuntu chroot → tmux → VSCode Server → CloudFlare Tunnel. 무공인IP + termux-wake-lock 패턴 |

### 신규 entity 5종 (세션 2~4 합계)

1. Evaluation_Skill_Genesis.md
2. GravityESS_Project.md
3. Tool_Guides_Collection_260411.md
4. Smartphone_Home_Server.md
5. (Wiki 진화 2차의 PaperResearch_Genesis.md는 이미 등록됨)

### 위키 통계 변화

- total_pages: 26 → **31** (+5 entity)
- 500_Technology entities: 6 → **10** (+4)
- 500_Technology sources: 10 (변동 없음)
- wiki-lint: **0 issues** (broken link 1개 발견 후 수정)

## 보안 경고 (사용자 즉시 조치 필요)

원본 Raw 파일 발췌 중 **민감 정보 3건 발견**. 위키 entity에는 모두 마스킹 처리:

### 1. OpenAI API 키 평문 노출
- **파일**: `Notion & Calender 연동 Make용 GPT 프롬프트.md`
- **노출**: `sk-proj-Iy5tup***` + `sk-proj-_wdUPq***` + `org-FG5rNW***`
- **조치**: OpenAI 대시보드에서 두 키 즉시 무효화 + 재발급

### 2. VSCode Server 비밀번호 평문 노출
- **파일**: `Phon으로 server만들기.md`
- **노출**: `park1095!@`
- **조치**: 즉시 변경. 다른 계정에 같은 비번 사용 시 모두 변경

### 3. SSH 공개키 노출
- **파일**: `Phon으로 server만들기.md`
- **노출**: `gei_personal@DESKTOP-415PRO0` 공개키
- **조치**: 위험도 낮음. 단, 노출된 공개키 페어 폐기 권장

## 100_AI 세션 진행 상황

| 세션 | 대상 | 상태 |
|:----:|------|:----:|
| 1 | 카탈로그 + PaperResearch Genesis | OK (Wiki 진화 2차) |
| **2** | 평가 에이전트 + GravityESS | **OK (이번 세션)** |
| **3** | 도구 가이드 5종 통합 | **OK (이번 세션)** |
| **4** | 홈서버 (Phon + 잠자는 폰) | **OK (이번 세션)** |
| 5 | 전기기기 GUI + Gemini 주가 + 여행 + 크롤링 | 대기 |
| 6 | OCR Grok + 도전율 + 아두이노 + yt-assets | 대기 |
| 7 | 100_AI 폴더 archive 이동 + 마무리 | 대기 |

**남은 unique 파일 (~10개)**:
- 전기기기 GUI 27KB / Gemini 주가 16KB / 여행 사이트 14KB / 251225 크롤링 10KB
- OCR Grok 99KB / 도전율 44KB / 아두이노 14KB / yt-assets 12KB
- + 빈 파일 1개 + Notion+Cal에 미흡수 부분

## 기타 폴더 (다음 옵션)

- **300_제일대학교** 354 md (가장 큼)
- **200_사업** 6 md + 12 pdf + 4 hwp (PDF MCP 활용)
- AI CLI Development 8 md
- 순서도 4 md
- 000_일단은 5 md

---

## 이전 세션 정보 (2026-04-11 Wiki 진화 -- PDF MCP + Raw 자료 추가 처리)

- **세션 시작**: 2026-04-11 (Tier-C 세션 1 위키 진화 직후)
- **세션 종료**: 2026-04-11 (PDF MCP entity + Raw 자료 카탈로그 + PaperResearch Genesis 완료)

## 이번 추가 작업 (Wiki 진화 2차) 성과

### A. PDF MCP 능력 재발견

이전 세션에서 "PDF 못 본다" 잘못 안내한 실수 → 이번에 도구 목록 재확인 → `mcp__plugin_pdf-viewer_pdf` 발견:
- `display_pdf` + `interact` 두 진입점
- 14 액션 + 9 주석 타입 + 좌표 시스템 + 폼 입력 + 저장
- **PDF_Viewer_MCP.md** entity 신규

→ **IMP-024 후보**: 도구 가용성 자가 검증 의무 (단정 금지)

### B. 000_Raw 신규 자료 (Obsidian Knowledge 668 파일)

사용자가 Obsidian 노트 vault 전체를 `001_Wiki_AI/000_Raw/`에 추가:
- 524 md + 80 png + 44 pdf + 4 hwp + 6 html + 6 csv = 668 파일
- 5 주요 폴더: 200_사업(757M), 300_제일대학교(169M), 100_AI 대화 저장(2.3M), Landom Report(15M), AI CLI Development

이번 세션 우선 처리: **100_AI 대화 저장** (42 md, 21 unique)

### C. 신규 위키 페이지 3종

1. **PDF_Viewer_MCP.md** (entity, 030_Work)
2. **260411_100_AI_Conversation_Archive_Catalog_V001.md** (source) -- 21 unique md 카탈로그 + 5 세션 점진 위키화 계획
3. **PaperResearch_Genesis.md** (entity) -- 002_AI_Project 연구자료 V1 (616KB) + V2 (10KB) 발췌. **Sci-Hub MCP 통합 시도 → Search & Log 전환 핵심 발견** (현재 PaperResearch 스킬의 기원)

### D. 위키 통계 변화

- total_pages: 23 → **26**
- 500_Technology entities: 4 → **6** (PDF Viewer + PaperResearch Genesis)
- 500_Technology sources: 9 → **10** (100_AI 대화 카탈로그)

### E. 미처리 (다음 세션)

**Raw 자료 점진 위키화**:
- 100_AI 대화 저장 세션 2: 평가 에이전트 89KB + GravityESS 51KB → 2 entity
- 100_AI 대화 저장 세션 3: Bkit 명령어 / Playwright e2e / Notion+Calendar 등 → 3 entity
- 100_AI 대화 저장 세션 4: 개발 시도 5개 통합 concept
- 100_AI 대화 저장 세션 5: 검색/리서치 6개 + 통합 + archive 이동 → 100% 완료

**기타 폴더 (524 md 중 482 미처리)**:
- 300_제일대학교 354 md (가장 큼, 다세션 필요)
- 200_사업 6 md + 12 pdf + 4 hwp (PDF MCP로 PDF 발췌 가능)
- AI CLI Development 8 md
- Landom Report 0 md (15M, 첨부 위주)

**(2).md 중복본 16개**:
- 사용자 승인 후 archive 이동 또는 삭제 권장

---

## 이전 세션 정보 (2026-04-11 Option E 세션 1 + Wiki 진화 완료)

- **세션 시작**: 2026-04-11 (Option E 세션 1 직후)
- **세션 종료**: 2026-04-11 (Tier-C 세션 1 결과 위키화 완료)
- **프로젝트**: 260410_Harness_Evolution

## 이번 추가 작업 (Wiki 진화) 성과

llm-wiki Mode 3로 Option E 세션 1 결과를 위키화:

### 갱신/신규 위키 페이지

1. **Navigator_Pattern_Library.md** (concept, 갱신):
   - 14 → 18 Navigator 통계 갱신
   - 적용 검증 표 14행 → 18행 (Tier-C 4 항목 추가)
   - 5 패턴 변형 4종 추가:
     - Operation Dispatcher: 5 ops 단순형 (btw) + 12 ops + 4 agents 대형 (pdca)
     - Branching + Linear: 9 규칙 다중 분기 (bkit-rules) + 7 Phase HARD-GATE (plan-plus)
   - 총 통계: 10488줄 / 25 Mermaid / 333 카드 → 13055줄 / 29 Mermaid / 457 카드

2. **260411_Tier_C_Session1_V001.md** (source, 신규):
   - Tier-C 세션 1 전체 기록
   - 4 Navigator 실측 데이터 + 작성 순서
   - SYSTEM_NAVIGATOR.md 자동 갱신 검증
   - 핵심 발견 4종 (scaffold 한계 + 12 ops 표현력 + 9 규칙 표현 + HARD-GATE 패턴)
   - IMP-022/023 후보 (scaffold 헤딩 파싱 + processType 일관성)

3. **index.md + log.md 갱신**:
   - total_pages 22 → 23
   - log 3개 신규 엔트리 (UPDATE concept + INGEST source + UPDATE index)

### 검증

- **wiki-lint**: 0 issues
- **회귀 0**: 기존 22 페이지 모두 보존

---

## 이전 세션 정보 (2026-04-11 Option E 세션 1 완료)

- **세션 시작**: 2026-04-11 (Warm Boot, Option G + H 이후)
- **세션 종료**: 2026-04-11 (Option E 세션 1: Tier-C 4개 신규 생성 완료)
- **프로젝트**: 260410_Harness_Evolution (Tier-C 100% 커버리지 진행)

## 이번 세션 (Option E 세션 1) 성과

Tier-C 8개 중 균형 잡힌 4개를 신규 생성. **전체 커버리지 14/22 → 18/22 (82%)**.

### 신규 Navigator 4개

| 스킬 | 줄 | 블럭 | Mermaid | click | 패턴 |
|------|-----|------|---------|-------|------|
| btw | 393 | 16 | 1 | 17 | Operation Dispatcher (5 ops) |
| plan-plus | 525 | 24 | 1 | 25 | Branching + Linear (7 Phase + HARD-GATE) |
| bkit-rules | 677 | 33 | 1 | 40 | Branching + Linear (9 규칙 + 다중 분기) |
| pdca | 972 | 51 | 1 | 52 | Operation Dispatcher (12 ops + 4 agents) |
| **합계** | **2567** | **124** | **4** | **134** | -- |

### SYSTEM_NAVIGATOR.md 자동 갱신 검증

PostToolUse 훅이 4 마커 모두 자동 채움:
- §1.2 navigator-diagram: OD_pdca/OD_btw + BL_bkit_rules/BL_plan_plus 추가
- §5.3 navigators-meta: 14 → 18 Navigator 표 자동 갱신
- §5.4 pattern-stats: Operation Dispatcher 2→4, Branching+Linear 2→4
- §9.0 gap-analysis: Tier-C 미생성 8 → 4 (50%)

총 줄수: 4244 → **4256** (+12, 자동 갱신만)

### 검증 결과

- **회귀 0**: 기존 14 Navigator + 8 AUTO 마커 모두 보존
- **이모티콘 0**: 4개 모두 PostToolUse emoji 차단 통과 (IMP-021 준수)
- **절대경로 0**: PostToolUse path-guard 통과
- **PostToolUse 훅 4회 성공**: 각 Navigator 작성 시 4 섹션 자동 갱신
- **블럭 카드 평균**: 31개/Navigator (15 기준 초과)
- **시간**: ~95분 (예상 ~115분 이내)

### 작성 순서 (작은 것 → 큰 것)

1. btw (~15분, 393줄, Operation Dispatcher 워밍업)
2. plan-plus (~20분, 525줄, Branching + Linear 첫 적용)
3. bkit-rules (~25분, 677줄, 9 규칙 다중 분기)
4. pdca (~35분, 972줄, 12 ops 가장 큼)

---

## 이전 세션 정보 (2026-04-11 Option G + H 완료)

- **세션 시작**: 2026-04-11 16:30 (Warm Boot, Option C 이후)
- **세션 종료**: 2026-04-11 (Option G + H + 000_Raw 점검 통합 완료)
- **프로젝트**: 260410_Harness_Evolution (지식 통합 + 각인 시스템 진화)

## 이번 세션 (Option G + H) 성과

3 작업 통합 처리 (~60분):

### Option H -- IMP-021 공식 기록

- `.harness/imprints.json`에 IMP-021 추가 (total_imprints: 20 → 21)
- 마크다운 표 마커는 ASCII 한정 (`O`/`-`/`[O]`/`[X]`/`Y`/`N`)
- PromptKit Navigator 작성 시 발견된 실수 (Option A 세션 3) 공식 학습

### 000_Raw 점검

- 4 하위 디렉토리(papers/reports/snapshots/transcripts) 모두 0 파일
- Raw 위키 진화 작업 불필요 (모든 외부 자료 이미 위키화 완료)

### Option G -- Wiki 진화 (llm-wiki Mode 3)

신규 위키 페이지 2개:
1. **SYSTEM_NAVIGATOR_Auto_Aggregation.md** (concept) -- 메타 문서 자동 집계 4 요소 패턴
2. **260411_Option_C_Auto_Aggregation_V001.md** (source) -- Option C 단일 세션 전체 기록

위키 통계: total_pages 20 → 22, 500_Technology 20 → 22

---

## 이전 세션 정보 (2026-04-11 Option C 완료)

- **세션 시작**: 2026-04-11 (Warm Boot, Option F 이후)
- **세션 종료**: 2026-04-11 (Option C: SYSTEM_NAVIGATOR.md 자동 재생성 완료)
- **프로젝트**: 260410_Harness_Evolution (Navigator 자동화 인프라 확대)

## 이번 세션 (Option C) 성과

SYSTEM_NAVIGATOR.md의 자동 갱신 영역을 **3.5% → ~14%**로 확대. 14 Navigator 메타데이터를 자동 수집하여 4개 신규 섹션 자동 갱신.

### 신규 reader 함수 4개 (helpers.js)

1. **`readNavigatorsMeta(cwd)`**: 14 Navigator 메타 표 + 통계(줄/Mermaid/블럭/클릭) + Tier 커버리지
2. **`readPatternStats(cwd)`**: 5 패턴 적용 분포 + 패턴별 상세
3. **`readGapAnalysis(cwd)`**: Tier-C 미생성 + 비표준 메타 + 검증 통과 요약
4. **`readNavigatorDiagram(cwd)`**: 14 Navigator를 5 패턴 subgraph로 그룹화한 자동 Mermaid

### 보조 함수 3개

- `parseSkillMetaTable(navContent, skillName, skillFm)`: ### 스킬 메타 표 파싱 (구버전 파일럿 fallback 포함)
- `normalizeProcessType(rawType)`: 다양한 표기를 5 패턴 + 변형 2종으로 정규화
- `collectNavigatorsData(cwd)`: 14 Navigator 단일 진입점 (4 reader 공통 사용)

### navigator-updater.js 확장

- `watchMap`을 단일 마커 → 다중 마커 배열로 확장 (`markers: [...], labels: [...]`)
- 단일 트리거(`.agents/skills/*/Navigator.md` 변경)가 4 마커 동시 갱신
- 마커 누락 시 스킵 (점진적 도입 안전)
- 안전 검증 (50% 임계값) 보존

### SYSTEM_NAVIGATOR.md 신규 4 섹션

| 섹션 | 마커 | 위치 |
|------|------|------|
| **§1.2 Navigator 시스템 체계도 (자동)** | `navigator-diagram` | 신규 |
| **§5.3 Navigator 카탈로그 (자동 집계)** | `navigators-meta` | 신규 |
| **§5.4 패턴 라이브러리 통계 (자동)** | `pattern-stats` | 신규 |
| **§9.0 자동 Gap 감지 (Navigator 검증)** | `gap-analysis` | 신규 |

### 통계 변화

| 항목 | Option C 이전 | Option C 이후 |
|------|--------------|--------------|
| SYSTEM_NAVIGATOR.md 줄수 | 4003 | **4244** (+241, +6%) |
| AUTO 마커 수 | 8 | **13** (+5, navigator 4 + 통계용 표 갱신) |
| 자동 갱신 영역 | 3.5% (~143줄) | **~14% (~600줄)** |
| helpers.js 줄수 | 1061 | **~1500** (신규 함수 7개 + 모듈 exports 7) |
| Reader 함수 수 | 6 | **10** (+4) |
| 모듈 exports | 22 | **29** (+7) |

### 검증 결과

- **회귀 0**: 기존 8 AUTO 마커 (skills-catalog/mcp-servers/commands/imprints/pre-tool-guard/bkit-scripts) 모두 보존
- **신규 4 마커 자동 채움**: navigators-meta(38행) + pattern-stats(7 패턴) + gap-analysis(검증 통과) + navigator-diagram(자동 Mermaid 5 subgraph)
- **훅 시뮬레이션 성공**:
  - Navigator.md 변경 → 4 마커 동시 갱신
  - SKILL.md 변경 → skills-catalog 단일 갱신 (회귀 0)
- **wiki-lint**: 0 issues
- **기존 콘텐츠 0 손실**: 9 Mermaid + 217 블럭 카드 + 갱신 이력 모두 그대로

### 14 Navigator 자동 분류 결과

| 패턴 | 적용 수 | 대표 |
|------|:------:|------|
| Linear Pipeline | 5 | PaperResearch, ServiceMaker, PromptKit, FileNameMaking, Mermaid_FlowChart |
| Operation Dispatcher | 2 | llm-wiki, harness-imprint |
| Track | 2 | HWPX_Master, DocKit |
| Branching + Linear | 2 | mdGuide, term-organizer |
| Branching + Phase | 1 | harness-architect |
| Conditional Step | 1 | VisualCapture |
| Phase + Recursive Loop | 1 | auto-error-recovery |

**참고**: 이전 세션 분류와 mdGuide가 "Branching + Linear"로 재분류됨 (이전: Linear Pipeline) -- 정확한 normalizeProcessType 매칭 결과

---

## 현재 시스템 상태 스냅샷

### Navigator 보유 (19개, Tier-S/A/B 100% + Tier-C 4/8)

| Tier | 보유 | 전체 | 비율 |
|:---:|:---:|:---:|:---:|
| S | 1 | 1 | 100% |
| A | 4 | 4 | 100% |
| B | 9 | 9 | 100% |
| C | 4 | 8 | **50%** |
| **합계** | **18** | **22** | **82%** |

(15 → 19로 +4 증가. Option E 세션 1 결과)

### SYSTEM_NAVIGATOR.md 자동화 인프라

- **AUTO 마커**: 8 → 13개 (+5)
- **Reader 함수**: 6 → 10개 (+4)
- **자동 갱신 영역**: 143줄 → ~600줄
- **navigator-updater.js**: 단일 마커 → 다중 마커 처리

### 각인 + 용어

- 각인: 21개 (IMP-001~021, IMP-021 NEW)
- 전문용어: 54개
- 위키 wiki-lint: 0 issues

### 미커밋 파일

- `.claude/hooks/navigator-updater-helpers.js` (신규 함수 7개 + exports 7)
- `.claude/hooks/navigator-updater.js` (watchMap 확장 + multi-marker 처리)
- `SYSTEM_NAVIGATOR.md` (신규 4 섹션 + AUTO 마커 4 + 회귀 0)
- `.harness/next-session.md` (이 파일 갱신)

---

## 다음 세션 작업 선택지

### 옵션 E 세션 2 (다음 권장): Tier-C 큰 것 + 중간 것

세션 1에서 4/8 완료. 남은 4개 중 큰 것 + 중간 것 우선.

**세션 2 권장 2개**:
- **zero-script-qa** (~1400줄, Linear Pipeline, 가장 큼)
- **development-pipeline** (~280줄, Linear Pipeline, 9 Phase)

**세션 3 권장 2개** (마지막):
- **code-review** (~300줄, Operation Dispatcher)
- **bkit-templates** (~360줄, Linear Pipeline)

세션 3 완료 후 Tier-C 8/8 = 100% (전체 22/22 = 100%) 달성 → 옵션 K (Tier-C Wiki 진화) 권장.

### 옵션 G: Wiki 진화 (Option C 결과 지식화)

llm-wiki Mode 3로 이번 작업을 위키화:
- "SYSTEM_NAVIGATOR Auto-Aggregation" 신규 concept
- 260411_Option_C_Auto_Aggregation source
- Navigator_Pattern_Library 통계 자동화 명시

### 옵션 I: 표준화 마이그레이션 (NEW)

harness-architect, llm-wiki를 ### 스킬 메타 표 구조로 전환 → PILOT_PATTERNS hardcoded fallback 제거. helpers.js 단순화 (~30분).

### 옵션 J: README/CHANGELOG 자동 집계 (NEW)

Auto-Aggregation 패턴 재사용. README.md가 하위 모듈 메타데이터를 자동 수집하도록 multi-marker 적용 (~60분).

### 참고: 완료된 옵션

- **Option D** (commit 안정화)
- **Option B** (scaffold 고도화 + IMP-019/020)
- **Option A 세션 1-3** (Tier-B 9/9)
- **Option F** (Wiki 진화 -- Tier-B 100% 마일스톤)
- **Option C** (SYSTEM_NAVIGATOR.md 자동 재생성)
- **Option G** (Wiki 진화 -- Option C 결과 지식화)
- **Option H** (IMP-021 공식 기록)
- **Option E 세션 1** (Tier-C 4개: btw/plan-plus/bkit-rules/pdca) ← 이번 세션

---

## Warm Boot 체크리스트 (에이전트 자동 수행)

### 1. 자동 훅
- SessionStart 훅이 `active-imprints.md` 갱신 (20개 각인 중 상위 10개 로드)

### 2. 맥락 복원 Read
1. **이 파일** (`.harness/next-session.md`) -- **첫 번째**
2. `docs/LogManagement/1st_Log.md` (시간순 대시보드)
3. `SYSTEM_NAVIGATOR.md` §5.3 Navigator 카탈로그 (자동 집계 결과 확인)
4. `001_Wiki_AI/500_Technology/concepts/Navigator_Pattern_Library.md`

### 3. Git 상태 확인
```bash
git status --short
git log --oneline -5
```

### 4. SYSTEM_NAVIGATOR.md 확인
```bash
wc -l SYSTEM_NAVIGATOR.md
grep -c "AUTO:.*:START" SYSTEM_NAVIGATOR.md
```

### 5. navigator-updater.js 동작 확인 (선택)
```bash
echo '{"tool_input":{"file_path":".agents/skills/term-organizer/term-organizer_Navigator.md"}}' | node .claude/hooks/navigator-updater.js
```

---

## 다음 세션 시작 명령어 제안

```
세션 재개. .harness/next-session.md 읽고 옵션 E (Tier-C 확장) 시작해줘.
```

또는 다른 옵션:

```
세션 재개. 옵션 G (Wiki 진화 -- Option C 결과 지식화) 시작해줘.
세션 재개. 옵션 H (IMP-021 공식 기록) 처리해줘.
```

---

## Option C 핵심 기술 노트

### multi-marker 트리거 처리

`navigator-updater.js`가 단일 트리거(`Navigator.md` 변경)로 4 마커를 동시 갱신할 수 있도록 확장:
- 기존: `marker: 'X'` 단일 필드
- 신규: `markers: ['A', 'B', 'C', 'D'], labels: [...]` 배열
- 마커별 순차 처리 + 누적 변경 → 단일 atomicWriteWithBackup

### 구버전 파일럿 fallback

harness-architect, llm-wiki는 `### 스킬 메타` 섹션이 없는 구버전 구조:
- `parseSkillMetaTable`이 hardcoded fallback 사용 (PILOT_PATTERNS)
- 향후 두 파일럿을 표준 메타 표로 마이그레이션 권장

### 자동 정규식 분류

`normalizeProcessType` 함수가 자유 형식 표기를 5 패턴 + 변형 2종으로 정규화:
- "Linear Pipeline (5-Step + Trigger 분기)" → "Linear Pipeline"
- "Operation Dispatcher (7 ops + 2 훅)" → "Operation Dispatcher"
- "Phase + Recursive Loop" → "Phase + Recursive Loop"

---

## 세션 간 연속성 보장

- 플래닝 문서: `C:\Users\pyu42\.claude\plans\noble-booping-peach.md`
- 각인: 20개 (IMP-001~020)
- 이 파일: `.harness/next-session.md` (이번 세션 갱신 완료)
- Navigator 자동화 인프라 확대 (8 → 13 AUTO 마커, 6 → 10 reader)

**다음 세션 종료 시에도 이 파일을 최신화할 것. (IMP-018)**
