---
name: llm-wiki
classification: workflow
classification-reason: "Integrated knowledge management + session handoff orchestration across cross-project boundary (005 -> 001_Wiki_AI)"
deprecation-risk: none
description: |
  LLM Wiki 지식 관리 + 세션 핸드오프 통합 스킬.
  Karpathy 3-layer(Raw/Wiki/Schema) 위에 세션 컨텍스트 증류를 결합.
  Claude Code가 위키 에이전트로서 마크다운 위키 구축 + 세션 지식 보존을 동시 수행합니다.
  WIKI_ROOT: ../001_Wiki_AI (PROJECT_ROOT 기준 상대경로)

  Triggers: 위키, wiki, 인제스트, ingest, 위키 검색, wiki query,
  위키 린트, wiki lint, 지식 정리, 지식베이스, knowledge base, 위키에 추가,
  저장해줘, 핸드오프, handoff, 세션 저장, 기록해줘, 지식화, 대화 저장,
  체크포인트, Warm Boot, next-session, 다음 세션

  Do NOT trigger for: 단순 파일 검색(Glob/Grep), 용어사전(term-organizer),
  각인(harness-imprint)
argument-hint: "[ingest|update|query|lint|status] [--mode=source|handoff|both] [source-path|query-text]"
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
hooks:
  Stop:
    - type: command
      command: "node .agents/skills/llm-wiki/scripts/wiki-log-append.js"
      timeout: 10000
---

# LLM-Wiki

Karpathy LLM Wiki 패턴 기반 지식 관리 스킬.
소스 문서를 위키 페이지로 변환(Ingest), 위키 검색 후 합성 응답(Query), 위키 구조 건강 검사(Lint)를 수행한다.

## Architecture

```
001_Wiki_AI/                       WIKI_ROOT = ../001_Wiki_AI
  CLAUDE.md                        Schema (위키 거버넌스)
  index.md                         카탈로그 (매 Ingest 재구성)
  log.md                           활동 이력 (append-only)
  000_Raw/                         Raw layer (미처리 입력 큐)
  Clippings/                       Raw layer (미처리 입력 큐, 000_Raw와 동일 취급)
  010_Verified/                    신뢰도: 검증된 정식 발행 문서
  001_General/                     KDC: 총류
  100_Philosophy/                  KDC: 철학
  200_Religion/                    KDC: 종교
  300_Social_Science/              KDC: 사회과학, 행정, 교육
  400_Natural_Science/             KDC: 자연과학
  500_Technology/                  KDC: 기술과학, AI, 에너지, 컴퓨터
  600_Arts/                        KDC: 예술
  700_Language/                    KDC: 어학
  800_Literature/                  KDC: 문학
  900_History/                     KDC: 역사, 지리
  990_Meta/                        위키 메타
    archive/                       원본 보관소 (지식화 완료된 원본 파일)
```

각 도메인 하위: `entities/` `concepts/` `sources/` `analysis/`

## Raw Layer 정책 (IMP-017)

**000_Raw/와 Clippings/는 미처리 입력 큐**로만 사용한다. 지식화(Ingest) 완료된 원본은 반드시 `990_Meta/archive/`로 이동하여 중앙 보관한다.

### 핵심 원칙

1. **입력 큐**: 새 원본 파일은 `000_Raw/` 또는 `Clippings/`에 배치
2. **지식화**: `wiki ingest` 실행 → sources/concepts/entities 페이지 생성
3. **원본 보관**: 지식화 완료 시 원본을 `990_Meta/archive/`로 이동 (삭제 금지)
4. **양방향 연결**:
   - 파생 위키 페이지 프론트매터에 `raw_source: "990_Meta/archive/<원본파일>"` 필수
   - 파생 위키 본문 하단에 "## Raw Source Archive" 섹션으로 명시적 링크
5. **재참조 가능**: 원본은 archive/에서 언제든 읽기 가능 (수정 금지)

### 한 원본에서 파생된 여러 위키

한 원본이 여러 위키 페이지의 소스가 될 수 있다. 예: `SYSTEM_NAVIGATOR.md` 원본 1개 → `Living_System_Mirror` concept + `260410_SYSTEM_NAVIGATOR_Optimization_V001` source + `Harness_Engineering` concept (3개 파생).

이 경우 **모든 파생 위키**가 동일한 `raw_source` 필드로 같은 원본을 참조한다. 이는 일종의 "역인덱스" 역할을 한다.

## Hybrid Mode (IMP-006: Obsidian CLI Integration)

모든 연산 시작 전 Phase -1을 실행하여 Obsidian CLI 사용 가능 여부를 감지한다.

### Phase -1: Obsidian 감지

```bash
node .agents/skills/llm-wiki/scripts/obsidian-detect.js "001_Wiki_AI"
```

결과에 따라:
- `mode: "cli"` -> Obsidian CLI 강화 모드 (아래 CLI 명령 매핑 사용)
- `mode: "filesystem"` -> 파일시스템 모드 (v2 방식)

`mode: "filesystem"` 시 사용자에게 선택 요청:
```
"Obsidian이 실행 중이지 않습니다.
 1) Obsidian을 켜고 다시 진행하시겠습니까? (CLI 강화 기능 사용)
 2) 그냥 진행하시겠습니까? (파일시스템 모드)"
```

### CLI 강화 명령 매핑

모든 CLI 명령에 `vault="001_Wiki_AI"` 파라미터를 추가한다.

| 위키 연산 | 파일시스템 모드 | CLI 강화 모드 |
|---|---|---|
| 검색 | Grep | `obsidian search query="keyword" vault="001_Wiki_AI"` |
| 검색 (컨텍스트) | Grep -C | `obsidian search:context query="keyword" vault="001_Wiki_AI"` |
| 파일 읽기 | Read | `obsidian read file="path" vault="001_Wiki_AI"` |
| 파일 생성 | Write | `obsidian create file="path" content="..." vault="001_Wiki_AI"` |
| 내용 추가 | Edit (append) | `obsidian append file="path" content="..." vault="001_Wiki_AI"` |
| 프론트매터 설정 | YAML 직접 작성 | `obsidian property:set file="path" property="key" value="val" vault="001_Wiki_AI"` |
| 프론트매터 읽기 | Read + 파싱 | `obsidian property:read file="path" property="key" vault="001_Wiki_AI"` |
| 역링크 | 불가 | `obsidian backlinks file="path" vault="001_Wiki_AI"` |
| 고아 페이지 | wiki-lint.js | `obsidian orphans vault="001_Wiki_AI"` |
| 깨진 링크 | wiki-lint.js | `obsidian deadends vault="001_Wiki_AI"` + `obsidian unresolved vault="001_Wiki_AI"` |
| 태그 목록 | Grep | `obsidian tags vault="001_Wiki_AI"` |
| 작업 목록 | Grep | `obsidian tasks vault="001_Wiki_AI"` |
| 템플릿 적용 | Write | `obsidian template:insert template="name" vault="001_Wiki_AI"` |
| Daily Note | Write (수동) | `obsidian daily:append content="..." vault="001_Wiki_AI"` |
| 파일 목록 | Glob | `obsidian files vault="001_Wiki_AI"` |
| 폴더 목록 | Glob | `obsidian folders vault="001_Wiki_AI"` |
| Vault 정보 | 불가 | `obsidian vault vault="001_Wiki_AI"` |

---

## Operations

### wiki ingest [--mode=MODE] [source-path]

통합 지식화 스킬. **Mode Selector**로 3가지 목적을 하나의 진입점에서 처리한다.

**Mode Selector**:

인자 없이 호출하면 사용자에게 번호 선택 UI 제공:

```
어떤 작업을 수행할까요?
1) Source only -- 원본 파일 → 위키 페이지 인제스트만 (기존 방식)
2) Session handoff only -- 대화 증류 + Projects/Log + 1st_Log + next-session.md
3) Both (권장) -- 대화를 위키 지식화 + 세션 핸드오프 동시 수행
```

직접 지정도 가능:
- `wiki ingest --mode=source <source-path>` -- Mode 1 강제
- `wiki ingest --mode=handoff` -- Mode 2 강제
- `wiki ingest --mode=both` -- Mode 3 강제

각 모드는 아래 세부 Phase 순서를 따른다.

---

### Mode 1: Source Only (기존 파일 인제스트)

원본 문서를 읽고 위키 페이지로 변환한다.

**Phase 0 -- 사전 점검**
- 소스 파일 존재 확인 (Read)
- log.md에서 동일 소스 중복 인제스트 여부 확인
- 50p+ PDF는 .txt 사전 추출 (AER-003)
- HWP/CSV는 cp949 + errors='replace' (IMP-001)

**Phase 1 -- 원본 읽기 + 기존 위키 탐색**
- Read로 소스 전체 읽기
- Glob + Grep으로 WIKI_ROOT 내 관련 기존 페이지 탐색 (AER-004: 읽기 먼저)

**Phase 2 -- 3축 분류 판정 (v3)**
- 축 1 (주제): KDC 어디에 해당하는가? (001~900)
- 축 2 (신뢰도): 010~070 중 어디인가?
  - 010 정식발행 / 020 공적기관 / 030 업무물 / 040 공문메일 / 050 프로젝트 / 060 영상 / 070 웹스크랩
- 축 3 (맥락): 어떤 프로젝트/업무 영역과 관련되는가? (프론트매터 context)

**Phase 3 -- 정본 위치 결정 + 페이지 생성**
- 정본 위치: "이 자료의 정체성은 무엇인가?" 기준
  - 논문 -> 010_Verified, 정부보고서 -> 020_Official, 프로젝트 결과 -> 050_Projects 등
- sources/YYMMDD_Subject_V001.md 생성 (소스 요약, 프론트매터에 domain + reliability + context)
- entities/ concepts/ 페이지 생성 또는 Edit으로 업데이트

**Phase 4 -- 바로가기(Shortcut) 생성 (v3 신규)**
- 정본 외 관련 분류 2-3곳 식별
- 각 관련 분류에 SHORTCUT.md 자동 생성
- SHORTCUT 형식: type=shortcut, canonical=정본경로, 본문 링크만 포함
- 파일명: `원본파일명_SHORTCUT.md`
- 사용자에게 바로가기 위치 확인 요청

**Phase 5 -- Raw 원본 archive 이동 (IMP-017 + IMP-023 강화)**

> **구조적 강제 (IMP-023, 2026-04-12)**: 이 Phase 는 entity/source 작성 직후 반드시 실행한다. **누락 시 하네스 위반**. 이전 세션들에서 stage-based 처리 흐름에서 이 단계가 체계적으로 빠져 438 MB가 Raw 에 방치되는 사고가 발생했음.

### 이동 방법 (우선순위 순)

**방법 1 (권장, 자동화)**: `wiki-pdf-stage.js archive-original` 명령 사용

```bash
# 기본 카테고리 (generic_processed)
node .claude/hooks/wiki-pdf-stage.js archive-original \
  "D:/OneDrive - 순천대학교/001_Wiki_AI/000_Raw/경로/파일명.pdf"

# 명시 카테고리
node .claude/hooks/wiki-pdf-stage.js archive-original \
  "D:/OneDrive - 순천대학교/001_Wiki_AI/000_Raw/경로/파일명.pdf" \
  200_사업_processed
```

이 명령은 자동으로:
- 위키 경로 검증 (000_Raw/ 또는 990_Meta/archive/ 만 허용)
- 파일명 충돌 시 타임스탬프 suffix 추가
- `os.rename` 원자적 이동
- stdout 으로 archive 경로 반환

**방법 2 (직접 파일 조작)**: Python `shutil.move` 또는 Node `fs.renameSync`
- 위 CLI 가 사용 불가 시에만
- 반드시 같은 카테고리 서브디렉토리 유지 (예: `200_사업_processed/`, `300_제일대_AI교재_processed/`)

### 필수 체크리스트 (모든 Ingest 완료 시)

1. **파일명 충돌 방지**: `<원본명>_<YYMMDD>.<ext>` 형식으로 suffix (자동 명령이 처리)
2. **frontmatter 갱신**: 파생 위키 페이지에 `raw_source: "990_Meta/archive/<카테고리>/<파일명>"` 추가
3. **본문 섹션 추가**: 파생 위키 하단에 "## Raw Source Archive" 섹션 + 원본 링크 + 메타데이터 (크기 / 획득 경로 / 지식화 날짜)
4. **다중 파생 처리**: 한 원본에서 여러 위키가 파생된 경우 **모든** 파생 위키에 동일 raw_source 설정
5. **용량 검증**: Phase 5 완료 후 Raw 폴더 용량이 파일 크기만큼 감소했는지 확인

### 누락 감지 (사후 검증)

세션 종료 전 Stop 훅 또는 수동 검증:

```bash
# Raw 폴더 총 용량 확인 (.obsidian 제외)
python -c "
import os
root = r'D:\OneDrive - 순천대학교\001_Wiki_AI\000_Raw'
total = 0
for dp, dirs, files in os.walk(root):
    if '.obsidian' in dp: continue
    for f in files:
        total += os.path.getsize(os.path.join(dp, f))
print(f'Raw 비-obsidian: {total/1024/1024:.1f} MB')
"
```

**기대값**: 미처리 파일만 남음 (= 새로 추가되어 아직 지식화되지 않은 파일). 지식화 완료된 파일이 남아 있으면 **IMP-023 위반**.

**Phase 6 -- 인덱스/로그 갱신**
- Glob으로 WIKI_ROOT 전체 스캔 후 index.md 재구성
- 정본은 [C], 바로가기는 [S]로 구분
- log.md에 INGEST 기록 append (정본 위치 + 바로가기 수 + raw_source 경로)

**Phase 7 -- 연계 스킬**
- 신규 전문용어 발견 시: term-organizer 연계
- 세션 종료 시: 내장된 Mode 2/3으로 자동 승격 가능 (사용자가 요청 시)

---

### Mode 2: Session Handoff Only (대화 증류 + 로그)

현재 대화 컨텍스트를 증류하여 세션 로그 + 1st_Log 대시보드 + next-session.md 진입점을 원자적으로 갱신한다. 위키 concept/source 페이지는 생성하지 않는다.

**Phase A -- Context Analysis (대화 증류)**
- 현재 대화 전체를 스캔하여 프로젝트 귀속 특정 (단일 또는 다중)
- 4요소 도출: **Goal / Actions / Result / Next Steps**
- Q&A 쌍을 `<details><summary>` 형식으로 임시 파일 생성 (`.tmp/qa_*.md`)
- 다중 프로젝트 감지 시 프로젝트별 Q&A 분리 + 임시 파일 N개

**Phase B -- handoff.py 호출**
- 경로: `.agents/skills/llm-wiki/scripts/handoff.py`
- 호출 시도 순서: **node 우선 확인 후 python** (IMP-002 준수). Windows에서 python PATH 미보장 시 AI가 직접 로직을 Node/Write로 수행하는 대체 경로 사용
- 자동 작업:
  - `Projects/YYMMDD_*/Log/session_YYMMDD_HHMM.md` 생성 (개별 로그)
  - `docs/LogManagement/1st_Log.md` 대시보드 업데이트 (하이퍼링크 포함)
  - 500줄 초과 시 `docs/archive/`로 자동 분할
- 다중 프로젝트 시 handoff.py 순차 호출 (병렬 금지, 쓰기 경쟁 방지)

```bash
# node 우선
node -e "require('child_process').execSync('python .agents/skills/llm-wiki/scripts/handoff.py ...', {stdio:'inherit'})"

# 또는 직접
python ".agents/skills/llm-wiki/scripts/handoff.py" \
  "Projects/YYMMDD_이름" "<Goal>" "<Actions>" "<Result>" "<Next>" "<QA임시파일경로>"
```

**Phase C -- .harness/next-session.md 갱신 (IMP-018)**
- 템플릿 구성: 이전 세션 정보 / 이번 세션 성과 / 현재 시스템 상태 / 다음 작업 선택지 / Warm Boot 체크리스트 / 각인 후보
- `atomicWriteWithBackup` 사용 (helpers.js 재사용) -- .bak 자동 생성
- 구조적 강제: 세션 종료 시 이 파일 갱신이 누락되면 하네스 위반

**Phase D -- 완료 보고 + 임시파일 정리**
- 생성/갱신된 파일 경로 요약 (session_*.md, 1st_Log.md, next-session.md)
- `.tmp/qa_*.md` 삭제
- IMP-019 후보 등 발견된 각인 기록 권장 사항 출력

---

### Mode 3: Both (통합 세션 종료, 권장 기본)

대화 증류 → 재사용 가능한 개념을 위키에 ingest → 세션 핸드오프를 순차적으로 수행. 세션 종료 시 하나의 호출로 3중 백업(위키 / 로그 / next-session) 완성.

**Phase A -- Context Analysis** (Mode 2와 동일)
- 4요소 도출 + QA 임시파일

**Phase A+ -- 재사용 개념 후보 식별**
- 증류 결과에서 프로젝트 특수 내용과 재사용 가능한 보편 개념 분리
- 재사용 후보 예: 설계 패턴, 워크플로우, 표준 매핑, 방법론
- 3-5개 정도가 적절. 너무 많으면 위키 노이즈

**Phase 1-6 -- Wiki Ingest** (Mode 1의 Phase 1-6 재사용)
- 각 재사용 개념마다 concept 페이지 생성
- 세션 전체 기록은 source 페이지 1개로 묶음 (`500_Technology/sources/YYMMDD_<session_theme>_V001.md`)
- `raw_source` 필드는 `Projects/YYMMDD_*/Log/session_YYMMDD_HHMM.md` 경로를 가리킴 (Raw archive 이동 생략 -- 대화에는 물리 원본 없음)
- index.md + log.md 갱신

**Phase B -- handoff.py 호출** (Mode 2와 동일)

**Phase C -- next-session.md 갱신** (Mode 2와 동일)

**Phase D -- 완료 보고 + 임시파일 정리**
- 3중 백업 결과 요약:
  - 위키 concepts/sources: N개 경로
  - 세션 로그 + 1st_Log 엔트리
  - next-session.md 진입점

### wiki update [page-path]

정본 페이지를 수정하고 바로가기를 동기화한다. (IMP-010)

**Phase 0 -- 정본 확인**
- 대상 페이지의 type이 shortcut이 아닌지 확인 (바로가기는 직접 수정 금지)
- 정본의 shortcuts[] 필드를 읽어 바로가기 목록 파악

**Phase 1 -- 정본 수정**
- 사용자 요청에 따라 정본 내용 Edit

**Phase 2 -- 바로가기 동기화**
- 정본의 title이 변경되었으면: 각 바로가기의 title도 업데이트
- 정본의 경로가 변경되었으면: 각 바로가기의 canonical 경로 + 본문 링크 업데이트
- 동기화 완료 후 log.md에 UPDATE + SYNC 기록

### wiki query [question]

위키 지식에 기반하여 질문에 답변한다.

**Phase 0 -- 인덱스 탐색**
- index.md 읽기 + 질문 키워드와 페이지 매칭

**Phase 1 -- 관련 페이지 검색**
- Grep으로 WIKI_ROOT 전체 검색
- 관련 페이지 최대 5개 선별 (컨텍스트 40% 제한 준수)

**Phase 2 -- 종합 답변**
- 선별 페이지 Read 후 정보 종합
- 각 주장에 출처 링크 명시: [페이지명](relative/path.md)
- 위키 데이터 부족 시: "Data Missing -- 관련 자료를 000_Raw/에 추가 후 wiki ingest 실행 권장"

**Phase 3 -- 로그**
- log.md에 QUERY 기록 append (질문 텍스트 포함)

### wiki lint

위키 구조 및 내용 건강 검사를 수행한다.

**Phase 1 -- 구조적 점검 (wiki-lint.js)**

```bash
node .agents/skills/llm-wiki/scripts/wiki-lint.js "../001_Wiki_AI"
```

점검 항목:
- 도메인 폴더 하위 4개 폴더(entities/concepts/sources/analysis) 존재 확인
- index.md 미등록 고아 페이지 감지
- 깨진 마크다운 링크(`[text](path)` 대상 파일 부재) 감지
- 파일명 규칙 위반 감지 (sources/analysis에 YYMMDD 없음, entities/concepts에 YYMMDD 있음)
- 필수 YAML 프론트매터 누락 감지 (title, domain, type, created, updated)

**Phase 2 -- 의미적 점검 (Claude 추론)**
- 동일 주제를 다루는 여러 페이지 간 모순 감지
- 90일 이상 미갱신 페이지 식별
- 많이 참조되지만 별도 페이지가 없는 개념/엔티티 식별
- 소스에는 있지만 위키에 미반영된 정보 갭 감지

**Phase 3 -- 보고서**
- CRITICAL / WARNING / INFO 분류
- 자동수정 가능 항목 표시 (빈 폴더 생성, index.md 등록 등)
- log.md에 LINT 기록 append

### wiki status

위키 현황 요약을 출력한다.

- 도메인별 페이지 수 집계
- 최근 인제스트 5건
- 미처리 소스 (000_Raw/에 있지만 sources/에 대응 페이지 없는 파일)
- 마지막 lint 일시

## Naming Rules

| 위치 | 파일명 형식 | 예시 |
|:---|:---|:---|
| entities/ | Descriptive_Name.md | Transformer.md, OpenAI.md |
| concepts/ | Descriptive_Name.md | Backpropagation.md, Fine_Tuning.md |
| sources/ | YYMMDD_Subject_V001.md | 260408_Attention_Is_All_You_Need_V001.md |
| analysis/ | YYMMDD_Subject_V001.md | 260408_Transformer_vs_RNN_V001.md |

## Link Rules

- 표준 마크다운 링크만 사용: `[텍스트](상대/경로.md)`
- `[[wikilink]]` 금지
- 모든 링크는 WIKI_ROOT 기준 상대경로
- 도메인 간 교차 참조 시: `[Transformer](../100_AI_ML/entities/Transformer.md)`

## Integration

| 연계 스킬 | 시점 | 조건 |
|:---|:---|:---|
| term-organizer | Ingest (Mode 1/3) 완료 | 신규 전문용어 발견 시 |
| PaperResearch | Pre-Ingest | 학술 검색 결과를 000_Raw/papers/에 저장 |
| mdGuide | Ingest/Lint | 위키 페이지 마크다운 품질 검증 |
| Mermaid_FlowChart | Analysis 생성 | 관계도 시각화 |
| harness-imprint | Mode 2/3 Phase D | 세션 중 발견된 각인 후보 기록 권장 |

> 세션 핸드오프는 Mode 2/3에 내장되었으므로 별도 스킬 연계 불필요.

## Constraints

- WIKI_ROOT = ../001_Wiki_AI (IMP-005)
- 000_Raw/ 수정 절대 금지
- 컨텍스트 사용량 40% 이하 유지 (Query 시 최대 5 페이지)
- 이모티콘 금지
- 절대경로 금지

### Session Handoff (Mode 2/3) 전용 제약

- `docs/LogManagement/1st_Log.md` AI 직접 편집 금지 -- 반드시 `handoff.py` 경유 (node 또는 python)
- 다중 프로젝트 시 handoff.py 순차 호출 의무 (병렬 금지)
- 다중 프로젝트 내용을 하나의 로그에 병합 금지
- Phase C (next-session.md 갱신) 누락 시 IMP-018 위반
- Python PATH 미보장 환경(IMP-002)에서는 node 우선 시도 후 AI가 직접 로직 수행
