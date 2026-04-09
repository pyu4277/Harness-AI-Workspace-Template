# Harness AI Workspace Template

> Claude Code + bkit v1.6.2 + Harness Engineering 4-Pillar.
> A workspace template that structurally enforces rules on AI agents, preventing violations through code rather than prompts.

[한국어 버전은 아래에 있습니다 (Korean version below)](#한국어-korean)

---

## What Is This

A workspace environment that solves 3 problems when using Claude Code for real work.

**Problem 1: AI ignores rules.**
Writing "don't use emojis" in CLAUDE.md is a request. The AI can ignore it.

**Problem 2: AI repeats the same mistakes.**
Starting a new conversation erases all context. Yesterday's fix is today's bug again.

**Problem 3: Knowledge doesn't accumulate.**
After 10 conversations, the AI still starts from zero every time.

---

## How It Works

### 1. Harness -- Structurally enforce rules

Rules are enforced by Node.js hooks, not prompts.

| Rule | Prompt approach | Harness approach |
|---|---|---|
| No emojis | "Don't use emojis" in CLAUDE.md | PostToolUse hook detects unicode and **blocks the write** |
| No absolute paths | "Don't hardcode paths" in CLAUDE.md | PostToolUse hook detects path patterns and **blocks the write** |
| Protect config files | "Don't touch settings" in CLAUDE.md | PreToolUse hook checks the path and **blocks access** |
| No rm -rf | "Don't run destructive commands" in CLAUDE.md | settings.local.json deny list **blocks execution** |

When the AI tries to break a rule, the hook physically prevents the action.

### 2. Imprints -- Remember mistakes, don't repeat them

Errors, retries, and painful experiences during work are recorded in `.harness/imprints.json`. When a similar situation is detected in the next conversation, the relevant experience is automatically recalled.

Example: "python command failed on Windows" -> recorded -> next time a script is written, "use node instead" is automatically activated.

9 imprints are currently registered.

### 3. LLM-Wiki -- Accumulate knowledge as a markdown wiki

Implements Andrej Karpathy's LLM Wiki pattern. Drop in a source document and the AI reads it, summarizes it, and creates structured wiki pages classified by entity and concept. Knowledge persists after the conversation ends.

3 operations:
- **Ingest**: Read source documents and create wiki pages
- **Query**: Search accumulated wiki knowledge and generate answers
- **Lint**: Check structural health of the wiki

Open the wiki folder in Obsidian to visually explore the knowledge graph.

---

## Architecture

3 layers:

```
[Harness Layer] -- What is forbidden, enforced structurally
  CLAUDE.md (66 lines)         Rule declarations
  .claude/hooks/ (5 scripts)   Node.js hooks that block rule violations
  .harness/imprints.json       Imprint system storing past mistakes (9 entries)

[bkit Layer] -- What order to follow
  bkit.config.json             PDCA workflow configuration
  .bkit/plugin/                Lifecycle hooks + libraries

[Skill Layer] -- What the AI can do
  .agents/skills/ (23)         Domain automation skills
  .agents/agents/ (31)         Agent definitions
  .agents/templates/ (28)      Design document templates
```

## Harness 4 Pillars

| Pillar | Role | Implementation |
|--------|------|---------------|
| Context | Auto-load rules at session start | CLAUDE.md + 7 support documents |
| CI/CD Gates | Block rule violations | PreToolUse/PostToolUse Node.js hooks |
| Tool Boundaries | Block dangerous commands | settings.local.json deny list |
| Feedback Loop | Record mistakes and reuse them | Imprint system (.harness/imprints.json) |

---

## Skills (23)

### Domain Skills (15)

| Skill | Purpose |
|---|---|
| llm-wiki | LLM Wiki knowledge management (Ingest/Query/Lint) + Obsidian CLI |
| HWPX_Master | Korean HWP document (.hwpx) creation/editing/extraction |
| DocKit | PDF/DOCX/PPTX document processing |
| PaperResearch | RISS + Google Scholar academic paper search |
| VisualCapture | Screenshot capture + AI image analysis |
| session-handoff | Session summary + log on conversation end |
| auto-error-recovery | Auto error analysis + recovery (max 3 retries) |
| ServiceMaker | Build new skills in 9 steps |
| PromptKit | 4-stage prompt engineering |
| Mermaid_FlowChart | Auto-generate Mermaid flowcharts |
| FileNameMaking | Batch rename files by semantic evaluation |
| mdGuide | Markdown quality validation |
| term-organizer | Technical glossary management |
| harness-architect | Apply harness 4-pillar to new projects |
| harness-imprint | Imprint recording and management |

### bkit Framework Skills (8)

| Skill | Purpose |
|---|---|
| pdca | Full PDCA cycle (Plan/Design/Do/Check/Report) |
| plan-plus | Brainstorming-enhanced planning |
| development-pipeline | 9-phase development pipeline |
| code-review | Code quality analysis |
| zero-script-qa | Docker log-based QA |
| btw | Improvement suggestion collection |
| bkit-rules | Auto-trigger rules |
| bkit-templates | Document templates |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/pyu4277/Harness-AI-Workspace-Template.git my-project
cd my-project

# 2. Run Claude Code
claude

# 3. The harness works automatically
```

## Customization

| File | What to change |
|---|---|
| CLAUDE.md | Add rules for your project |
| code-convention.md | Adjust to your team's coding style |
| adr.md | Add ADR-NNN for new architecture decisions |
| .claude/hooks/*.js | Customize forbidden patterns / allowed paths |
| settings.local.json | Adjust command deny list |

## Requirements

- Windows 11
- Node.js v20+
- Claude Code
- Obsidian v1.12.4+ (optional, for LLM-Wiki)

## License

MIT

## Credits

- Harness Engineering 4-Pillar: Mitchell Hashimoto (2026.02), Martin Fowler
- LLM Wiki pattern: Andrej Karpathy (2026.04)
- bkit framework: bkit v1.6.2

---

# 한국어 (Korean)

> Claude Code + bkit v1.6.2 + Harness Engineering 4-Pillar.
> AI 에이전트가 작업 규칙을 어기지 못하도록 구조적으로 강제하는 작업 환경 템플릿.

---

## 이 시스템은 무엇인가

Claude Code를 업무에 활용할 때 발생하는 3가지 문제를 해결하는 작업 환경입니다.

**문제 1: AI가 규칙을 무시한다**
CLAUDE.md에 "이모티콘 쓰지 마"라고 적어도, AI는 이를 무시할 수 있습니다. 프롬프트에 적힌 규칙은 부탁이기 때문입니다.

**문제 2: AI가 같은 실수를 반복한다**
새 대화를 시작하면 이전 대화의 맥락이 사라집니다. 어제 해결한 문제를 오늘 또 겪습니다.

**문제 3: 작업할수록 지식이 쌓이지 않는다**
10번 대화해도 매번 처음부터 시작합니다. 이전에 정리한 내용을 다음 대화에서 활용할 수 없습니다.

---

## 어떻게 해결하는가

### 1. 하네스 (Harness) -- 규칙을 구조적으로 강제

규칙을 프롬프트(부탁)가 아닌 Node.js 훅(강제)으로 실행합니다.

| 규칙 | 프롬프트 방식 | 하네스 방식 |
|---|---|---|
| 이모티콘 금지 | CLAUDE.md에 "쓰지 마" | PostToolUse 훅이 유니코드 감지 후 **저장 차단** |
| 절대경로 금지 | CLAUDE.md에 "쓰지 마" | PostToolUse 훅이 경로 패턴 감지 후 **저장 차단** |
| 설정 파일 보호 | CLAUDE.md에 "건드리지 마" | PreToolUse 훅이 경로 검사 후 **접근 차단** |
| rm -rf 금지 | CLAUDE.md에 "실행하지 마" | settings.local.json deny 목록으로 **실행 차단** |

AI가 규칙을 어기려고 하면, 훅이 해당 동작을 물리적으로 막습니다.

### 2. 각인 (Imprint) -- 실수를 기억하고 반복하지 않음

AI가 작업 중 겪은 에러, 재시도, 번거로운 경험을 `.harness/imprints.json`에 기록합니다. 다음 대화에서 비슷한 상황이 감지되면 해당 경험을 자동으로 떠올립니다.

예시: "Windows에서 python 명령이 실패했다" -> 기록 -> 다음에 스크립트를 작성할 때 자동으로 "node를 우선 사용하라"는 경험이 활성화됩니다.

현재 9개의 각인이 등록되어 있습니다.

### 3. LLM-Wiki -- 지식을 마크다운 위키로 축적

Andrej Karpathy가 제안한 LLM Wiki 패턴을 구현했습니다. 원본 문서를 넣으면 AI가 읽고, 요약하고, 엔티티/개념별로 분류하여 마크다운 위키 페이지를 생성합니다. 대화가 끝나도 위키에 지식이 남습니다.

3가지 연산을 지원합니다:
- **Ingest**: 원본 문서를 읽어서 위키 페이지로 변환
- **Query**: 위키에 축적된 지식을 검색하여 답변 생성
- **Lint**: 위키의 구조적 건강 상태를 점검

Obsidian에서 위키 폴더를 열면 그래프 뷰로 지식 연결 구조를 시각적으로 확인할 수 있습니다.

---

## 시스템 구조

3개 계층으로 구성되어 있습니다.

```
[하네스 계층] -- 무엇이 금지인지 강제
  CLAUDE.md (66줄)           작업 규칙 선언
  .claude/hooks/ (5개)       Node.js 훅으로 규칙 위반 차단
  .harness/imprints.json     과거 실수를 기억하는 각인 시스템 (9개)

[bkit 계층] -- 작업 순서를 관리
  bkit.config.json           PDCA 워크플로우 설정
  .bkit/plugin/              라이프사이클 훅 + 라이브러리

[스킬 계층] -- 반복 작업을 자동화
  .agents/skills/ (23개)     도메인별 자동화 스킬
  .agents/agents/ (31개)     에이전트 정의
  .agents/templates/ (28종)  설계 문서 템플릿
```

## 하네스 4기둥

| 기둥 | 역할 | 구현 방법 |
|------|------|--------|
| 컨텍스트 | 매 세션 시작 시 규칙 자동 로드 | CLAUDE.md + 지원 문서 7개 |
| CI/CD 게이트 | 규칙 위반 시 동작 차단 | PreToolUse/PostToolUse Node.js 훅 |
| 도구 경계 | 위험 명령어 실행 차단 | settings.local.json deny 목록 |
| 피드백 루프 | 실수를 기록하고 다음에 활용 | 각인 시스템 (.harness/imprints.json) |

---

## 포함된 스킬 (23개)

### 도메인 스킬 (15개)

| 스킬 | 용도 |
|---|---|
| llm-wiki | LLM Wiki 지식 관리 (Ingest/Query/Lint) + Obsidian CLI 연동 |
| HWPX_Master | 한글 문서(.hwpx) 생성/수정/추출/자동화 |
| DocKit | PDF/DOCX/PPTX 문서 처리 |
| PaperResearch | RISS + Google Scholar 학술 논문 검색 |
| VisualCapture | 화면 캡처 + AI 이미지 분석 |
| session-handoff | 세션 종료 시 작업 내용 요약 + 로그 저장 |
| auto-error-recovery | 에러 발생 시 원인 분석 + 자동 복구 (최대 3회) |
| ServiceMaker | 새 스킬을 9단계 절차로 개발 |
| PromptKit | 프롬프트를 4단계로 개선 |
| Mermaid_FlowChart | Mermaid 흐름도 자동 생성 |
| FileNameMaking | 파일명을 의미 기반으로 일괄 변경 |
| mdGuide | 마크다운 문서 품질 검증 |
| term-organizer | 전문용어 사전 관리 |
| harness-architect | 새 프로젝트에 하네스 4기둥 자동 적용 |
| harness-imprint | 각인 기록 및 관리 |

### bkit 프레임워크 스킬 (8개)

| 스킬 | 용도 |
|---|---|
| pdca | 기획/설계/실행/검증/보고 전체 주기 관리 |
| plan-plus | 브레인스토밍 강화 기획 |
| development-pipeline | 9단계 개발 파이프라인 |
| code-review | 코드 품질 분석 |
| zero-script-qa | Docker 로그 기반 QA |
| btw | 개선 제안 수집 |
| bkit-rules | 자동 트리거 규칙 |
| bkit-templates | 문서 템플릿 |

---

## 빠른 시작

```bash
# 1. 클론
git clone https://github.com/pyu4277/Harness-AI-Workspace-Template.git my-project
cd my-project

# 2. Claude Code 실행
claude

# 3. 하네스가 자동으로 작동합니다
```

## 커스터마이징

| 파일 | 수정 내용 |
|---|---|
| CLAUDE.md | 프로젝트에 맞는 규칙 추가 |
| code-convention.md | 팀 코딩 스타일에 맞게 수정 |
| adr.md | 새 아키텍처 결정 시 ADR-NNN 추가 |
| .claude/hooks/*.js | 금지 패턴/허용 경로 변경 |
| settings.local.json | 명령어 deny 목록 조정 |

## 요구 사항

- Windows 11
- Node.js v20+
- Claude Code
- Obsidian v1.12.4+ (LLM-Wiki 사용 시 선택사항)

## 라이선스

MIT

## 출처

- 하네스 엔지니어링 4기둥: Mitchell Hashimoto (2026.02), Martin Fowler
- LLM Wiki 패턴: Andrej Karpathy (2026.04)
- bkit 프레임워크: bkit v1.6.2
