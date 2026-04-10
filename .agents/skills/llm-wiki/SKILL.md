---
name: llm-wiki
classification: workflow
classification-reason: "3-operation orchestration (Ingest/Query/Lint) across cross-project boundary (005 -> 001_Wiki_AI)"
deprecation-risk: none
description: |
  LLM Wiki 지식 관리 스킬. Karpathy 3-layer(Raw/Wiki/Schema) + 3-operation(Ingest/Query/Lint) 패턴.
  Claude Code가 위키 에이전트로서 마크다운 위키를 점진적으로 구축/유지합니다.
  WIKI_ROOT: ../001_Wiki_AI (PROJECT_ROOT 기준 상대경로)

  Triggers: 위키, wiki, 인제스트, ingest, 위키 검색, wiki query,
  위키 린트, wiki lint, 지식 정리, 지식베이스, knowledge base, 위키에 추가

  Do NOT trigger for: 단순 파일 검색(Glob/Grep), 용어사전(term-organizer),
  세션 로그(session-handoff), 각인(harness-imprint)
argument-hint: "[ingest|query|lint|status] [source-path|query-text]"
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
  000_Raw/                         Raw layer (불변 소스)
  Clippings/                       Raw layer (불변 소스, 000_Raw와 동일 취급)
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
```

각 도메인 하위: `entities/` `concepts/` `sources/` `analysis/`

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

### wiki ingest [source-path]

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

**Phase 5 -- 인덱스/로그 갱신**
- Glob으로 WIKI_ROOT 전체 스캔 후 index.md 재구성
- 정본은 [C], 바로가기는 [S]로 구분
- log.md에 INGEST 기록 append (정본 위치 + 바로가기 수)

**Phase 6 -- 연계 스킬**
- 신규 전문용어 발견 시: term-organizer 연계
- 세션 종료 시: session-handoff에 위키 연산 요약 포함

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
| term-organizer | Ingest 완료 | 신규 전문용어 발견 시 |
| PaperResearch | Pre-Ingest | 학술 검색 결과를 000_Raw/papers/에 저장 |
| session-handoff | 연산 종료 | 위키 연산 요약을 세션 로그에 포함 |
| mdGuide | Ingest/Lint | 위키 페이지 마크다운 품질 검증 |
| Mermaid_FlowChart | Analysis 생성 | 관계도 시각화 |

## Constraints

- WIKI_ROOT = ../001_Wiki_AI (IMP-005)
- 000_Raw/ 수정 절대 금지
- 컨텍스트 사용량 40% 이하 유지 (Query 시 최대 5 페이지)
- 이모티콘 금지
- 절대경로 금지
