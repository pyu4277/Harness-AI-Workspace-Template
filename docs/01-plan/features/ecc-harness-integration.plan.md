# ECC-Harness 통합 설계문서 (6종 통합본)

> Harness Architect Phase 3 산출물. Tier 3 Enterprise.
> 프로젝트: Harness-AI-Workspace-ECC-Unified
> 작성일: 2026-04-10

---

## 문서 1: 사업 기획서

### 하네스 엔지니어링 적용

| 기둥 | 이 문서에서의 역할 |
|------|-------------------|
| 기둥1 (컨텍스트) | 통합 범위와 우선순위 정의 -> CLAUDE.md 반영 |
| 기둥2 (CI/CD) | 충돌 시 Harness 우선 원칙 -> Hook 실행 순서 강제 |
| 기둥3 (도구경계) | ECC 훅 비활성화 범위 -> ECC_HOOK_PROFILE 설정 |
| 기둥4 (피드백) | 통합 후 문제 발생 시 각인 등록 |

### WHY

005_AI_Project(Harness)는 한국 대학 연구/행정 특화 자동화 플랫폼이다. ECC(Everything Claude Code)는 147K+ stars의 범용 AI 개발 도구이다. ECC의 181개 스킬, 47개 에이전트, 보안 스캐너, Instinct 학습 시스템을 Harness에 통합하면 도메인 특화 + 범용 개발 자동화를 모두 갖춘 플랫폼이 된다.

### WHAT

ECC v1.10.0의 전체 기능을 005_AI_Project에 통합한다. Harness가 모든 충돌에서 우선한다.

### SCOPE

**IN**:
- ECC 181 스킬 + 47 에이전트 + 81 커맨드 + 89 규칙 (글로벌 레벨, 이미 설치됨)
- ECC 33 Hook Scripts (선별적 활성화)
- AgentShield 보안 스캐너 (npx로 실행)
- Instinct 학습 시스템 (세션 평가 + 패턴 추출)
- 비용 추적 (cost-tracker)
- Bash 감사 로그 (command-log)

**OUT**:
- ECC session-start (Harness imprint 시스템과 충돌)
- ECC config-protection (Harness pre-tool-guard가 담당)
- ECC quality-gate, design-quality-check (Harness post-tool-validate가 담당)
- ECC format-typecheck, console-log-check (Python 중심 프로젝트에서 불필요)
- ECC suggest-compact, governance-capture, observe (Harness bkit가 담당)
- ECC pre-compact (Harness bkit context-compaction이 담당)

---

## 문서 2: 요구사항 정의서

### 기능 요구사항 (FR)

| ID | 요구사항 | 검증 방법 |
|---|---|---|
| FR-001 | ECC 훅 중 Harness와 충돌하는 것은 비활성화 | ECC_HOOK_PROFILE=minimal 설정 후 SessionStart에서 Harness만 실행 확인 |
| FR-002 | ECC session-start는 완전 비활성화 | ECC_DISABLED_HOOKS=session:start 설정 후 ~/.claude/session-data/에 새 부트스트랩 없음 확인 |
| FR-003 | Harness pre-tool-guard가 Write/Edit의 첫 번째 가드 | minimal 프로필에서 ECC Write/Edit 훅 전부 비활성화 확인 |
| FR-004 | ECC Stop 훅 3개(session-end, evaluate-session, cost-tracker)는 async로 유지 | Stop 시 Harness unified-stop(sync) 완료 후 ECC 3개가 백그라운드 실행 확인 |
| FR-005 | /code-review는 Harness 버전 실행 | /code-review 입력 시 한국어 출력 확인 (프로젝트 레벨 우선) |
| FR-006 | deny 목록에 sudo, chmod 777, >/dev/ 추가 | 해당 명령 실행 시 차단 확인 |
| FR-007 | ECC 규칙(rules/)과 Harness CLAUDE.md 공존 | 한국어 출력 규칙이 ECC 영어 규칙보다 우선 적용 확인 |

### 비기능 요구사항 (NFR)

| ID | 요구사항 | 위반 시 대응 |
|---|---|---|
| NFR-001 | Stop 시간 10초 이내 | ECC async 훅 3개의 timeout이 각 10초. 총 시간 초과 시 ECC 훅 비활성화 |
| NFR-002 | 세션 시작 시간 5초 이내 | ECC session-start 비활성화로 보장 |
| NFR-003 | OneDrive 동기화 호환 | 모든 설정은 프로젝트 내부 파일로 관리 (심볼릭 링크 불가) |

---

## 문서 3: 아키텍처 설계서

### 2-Layer Hook Architecture

```
[Layer 1: Global -- ECC]
C:\Users\pyu42\.claude\settings.json
  -> scripts/hooks/ (33 scripts)
  -> ECC_HOOK_PROFILE=minimal로 대부분 비활성화
  -> 생존: block-no-verify, auto-tmux-dev, command-log(2), session-end, evaluate-session, cost-tracker, session-end-marker

[Layer 2: Project -- Harness]
D:\OneDrive - ...\005_AI_Project\.claude\hooks.json
  -> .claude/hooks/ (5 harness scripts)
  -> .bkit/plugin/scripts/ (12 bkit scripts)
  -> 전부 활성

실행 순서: Layer 1 -> Layer 2
Block 결정: 어느 Layer에서든 block 반환 시 작업 중단
```

### 의존성 규칙

- Harness CLAUDE.md > ECC rules/ (프로젝트 레벨이 글로벌 우선)
- Harness hooks.json > ECC settings.json hooks (프로젝트가 마지막에 실행)
- Harness .agents/skills/ > ECC ~/.claude/skills/ (프로젝트 레벨이 글로벌 섀도잉)
- Harness settings.local.json deny > 모든 도구 (deny는 어느 레벨이든 최우선)

### 보안 경계

- pre-tool-guard.js: Write/Edit 경로 화이트리스트 (Harness 전용)
- post-tool-validate.js: 이모티콘/절대경로/시크릿/위험함수 감지 (Harness 전용)
- ECC block-no-verify: git --no-verify 방지 (ECC 전용, Harness에 없는 기능)
- settings.local.json deny: rm -rf, git push --force, curl, wget, sudo, chmod 777, >/dev/ (통합)

---

## 문서 4: SRS (상세 요구사항)

### 4-1. settings.local.json 변경 상세

현재:
```json
{
  "permissions": {
    "deny": ["Bash(rm -rf *)", "Bash(rm -r *)", "Bash(git push --force*)", "Bash(git reset --hard*)", "Bash(curl *)", "Bash(wget *)"]
  }
}
```

변경 후:
```json
{
  "permissions": {
    "deny": ["Bash(rm -rf *)", "Bash(rm -r *)", "Bash(git push --force*)", "Bash(git reset --hard*)", "Bash(curl *)", "Bash(wget *)", "Bash(sudo *)", "Bash(chmod 777 *)", "Bash(*>/dev/*)"]
  },
  "env": {
    "ECC_HOOK_PROFILE": "minimal",
    "ECC_DISABLED_HOOKS": "session:start"
  }
}
```

### 4-2. CLAUDE.md 변경 상세

참조 문서 섹션에 1줄 추가:
```
- ECC 통합: ECC_HOOK_PROFILE=minimal, ECC_DISABLED_HOOKS=session:start (하네스 우선, ADR-007)
```

### 4-3. ADR-007 추가

adr.md에 ECC 통합 아키텍처 결정 기록 추가.

### 4-4. IMP-011 각인

ECC 통합 패턴 각인 등록.

---

## 문서 5: 순서도 및 절차도

### Hook 실행 순서 (SessionStart)

```
Session Start
  |
  +-- [ECC Layer 1]
  |     session:start -> DISABLED (ECC_DISABLED_HOOKS)
  |
  +-- [Harness Layer 2]
        imprint-session-start.js -> active-imprints.md 갱신
        bkit session-start.js -> bkit 상태 로드
```

### Hook 실행 순서 (PreToolUse Write/Edit)

```
Write/Edit 시도
  |
  +-- [ECC Layer 1]
  |     config-protection -> DISABLED (minimal profile)
  |     suggest-compact -> DISABLED (minimal profile)
  |     observe -> DISABLED (minimal profile)
  |     governance-capture -> DISABLED (minimal profile)
  |
  +-- [Harness Layer 2]
        pre-tool-guard.js -> 경로 화이트리스트 검사
        bkit pre-write.js -> bkit 쓰기 검증
  |
  +-- 실행 또는 차단
```

### Hook 실행 순서 (Stop)

```
Response End (Stop)
  |
  +-- [ECC Layer 1]
  |     stop:session-end (async, 10s) -> 세션 상태 저장
  |     stop:evaluate-session (async, 10s) -> Instinct 패턴 추출
  |     stop:cost-tracker (async, 10s) -> 토큰 비용 기록
  |
  +-- [Harness Layer 2]
        unified-stop.js (sync, 10s) -> 스킬/에이전트/bkit 정리
  |
  +-- 완료
```

---

## 문서 6: 통합설계서

### 충돌 해결 매트릭스

| # | 충돌 | ECC 기능 | Harness 기능 | 결정 | 구현 |
|---|---|---|---|---|---|
| 1 | SessionStart | session-start-bootstrap | imprint-session-start | KEEP_HARNESS | ECC_DISABLED_HOOKS=session:start |
| 2 | PreToolUse Write | config-protection | pre-tool-guard | KEEP_HARNESS | minimal profile |
| 3 | PreToolUse compact | suggest-compact | bkit context-compaction | KEEP_HARNESS | minimal profile |
| 4 | PostToolUse Write | quality-gate + design-check | post-tool-validate | KEEP_HARNESS | minimal profile |
| 5 | PostToolUse observe | continuous-learning observe | bkit unified-write-post | KEEP_HARNESS | minimal profile |
| 6 | Stop format | stop:format-typecheck | unified-stop | KEEP_HARNESS | minimal profile |
| 7 | Stop console | stop:check-console-log | post-tool-validate | KEEP_HARNESS | minimal profile |
| 8 | PreCompact | pre:compact | bkit context-compaction | KEEP_HARNESS | minimal profile |
| 9 | code-review | ECC code-review | Harness code-review | KEEP_HARNESS | 프로젝트 레벨 자동 우선 |
| 10 | Rules 언어 | English-first | Korean-first | KEEP_HARNESS | 프로젝트 CLAUDE.md 자동 우선 |

### ECC에서 Harness로 가져오는 기능

| 기능 | ECC Hook/Tool | 역할 | 충돌 여부 |
|---|---|---|---|
| git hook 보호 | block-no-verify | --no-verify 차단 | 없음 |
| tmux 개발 서버 | auto-tmux-dev | 장시간 명령 tmux 실행 | 없음 |
| Bash 감사 로그 | command-log-audit | 모든 bash 명령 로깅 | 없음 |
| 비용 추적 | command-log-cost + cost-tracker | 토큰 비용 추적 | 없음 |
| 세션 영속성 | session-end | 세션 상태 저장 | 없음 |
| Instinct 학습 | evaluate-session | 패턴 자동 추출 | 없음 |
| 세션 종료 마커 | session-end-marker | 세션 종료 기록 | 없음 |
| AgentShield | npx ecc-agentshield | 보안 스캐너 | 없음 |
| 181 스킬 | ~/.claude/skills/ | 범용 개발 자동화 | 1개 섀도잉 (code-review) |
| 47 에이전트 | ~/.claude/agents/ | 특화 서브에이전트 | 없음 |
| 89 규칙 | ~/.claude/rules/ | 언어별 코딩 규칙 | 공존 (프로젝트 우선) |

---

## 검증 계획

| # | 검증 항목 | 방법 | 기대 결과 |
|---|---|---|---|
| 1 | Harness 세션 초기화 | 세션 시작 -> active-imprints.md 타임스탬프 확인 | 갱신됨 |
| 2 | ECC 세션 초기화 비활성 | session-data/ 확인 | 새 부트스트랩 없음 |
| 3 | Write 경로 보호 | .claude/settings.json에 Write 시도 | pre-tool-guard가 차단 |
| 4 | /code-review 한국어 | /code-review 실행 | 한국어 출력 |
| 5 | Stop 완료 | 응답 종료 후 대기 | unified-stop + ECC async 모두 완료 |
| 6 | git --no-verify 차단 | git commit --no-verify 시도 | ECC block-no-verify가 차단 |
| 7 | sudo 차단 | sudo 명령 시도 | settings.local.json deny가 차단 |
| 8 | AgentShield 스캔 | npx ecc-agentshield scan | A등급 결과 |
