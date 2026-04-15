# 아키텍처 결정 기록 (Architecture Decision Records)

> 005_AI_Project의 주요 아키텍처 결정을 기록한다.
> 새 결정 시 이 파일 하단에 ADR-NNN 형식으로 추가.

---

## ADR-001: bkit 훅과 하네스 훅 공존 채택

**상태**: 채택 (2026-04-07)

**컨텍스트**:
004_AI_Project는 bkit v1.6.2의 48개 JS 훅 스크립트로 PDCA 워크플로우를 관리한다. 005에서 하네스 엔지니어링 4기둥을 적용할 때, bkit 훅을 교체하면 PDCA 기능이 손실된다.

**결정**:
hooks.json에서 하네스 가드 훅(bash)을 bkit 훅(node) 앞에 배치하여 공존시킨다. 하네스 훅이 block 판정 시 bkit 훅은 실행되지 않는다.

**근거**:
- bkit의 PDCA 워크플로우 기능 보존
- 하네스의 거버넌스 강제 기능 추가
- 관심사 분리: 하네스=거버넌스, bkit=워크플로우

**결과**:
PreToolUse/PostToolUse의 Write|Edit 매처에서 [1]하네스 [2]bkit 순서로 실행.

---

## ADR-002: CLAUDE.md 60줄 + 지원 문서 7개 분리

**상태**: 채택 (2026-04-07)

**컨텍스트**:
004의 CLAUDE.md는 약 450줄로, 하네스 엔지니어링의 60줄 규칙을 6.5배 초과했다. 매 세션마다 전체가 로드되어 컨텍스트 예산을 소모한다.

**결정**:
핵심 규칙(11줄), 절대 금지(7줄), 참조 문서(9줄), 에이전트 운영(3줄) = 약 46줄만 CLAUDE.md에 유지. 나머지는 `docs/support/` 7개 파일로 분리.

**근거**:
- 매 세션 컨텍스트 예산 절감
- "신입사원 온보딩 문서" 역할에 집중
- 상세 규칙은 필요 시 Read로 참조

**결과**:
CLAUDE.md 46줄 (14줄 성장 여유). 지원 문서 7개로 004의 전체 내용 보존.

---

## ADR-003: 패키지 설치(pip/npm) 에이전트 허용 유지

**상태**: 채택 (2026-04-07)

**컨텍스트**:
하네스 최소 권한 원칙에 따르면 pip install/npm install을 deny로 차단하는 것이 이상적이다. 그러나 이 프로젝트는 연구/행정 자동화 목적으로 다양한 Python 라이브러리를 빈번하게 사용한다.

**결정**:
pip install, npm install은 settings.json allowedTools에 유지하되, curl/wget은 deny로 차단한다.

**근거**:
- 연구 프로젝트 특성상 라이브러리 설치 빈도가 높음
- 사용자가 매번 터미널로 전환하면 워크플로우 단절
- curl/wget은 외부 다운로드 차단이라는 별도 보안 목적

**결과**:
`Bash(pip *)`, `Bash(npm *)` 허용. `Bash(curl *)`, `Bash(wget *)` deny.

---

## ADR-004: 각인(Imprint) 시스템 도입 -- 위키 상위의 구조적 학습

**상태**: 채택 (2026-04-07)

**컨텍스트**:
기존 학습 메커니즘(AER, session-handoff, CLAUDE.md 자기 진화)은 모두 "기록" 수준이다. 기록은 찾아봐야 하고, 에이전트가 자발적으로 참조하지 않는다. 같은 실수가 다른 세션에서 반복될 수 있다.

**결정**:
`.harness/imprints.json`에 구조화된 각인(상황/고투/해결/원칙)을 저장하고, SessionStart 훅으로 상위 각인을 자동 주입, UserPromptSubmit 훅으로 키워드 매칭 시 자동 회수하는 시스템 도입.

**근거**:
- 기록(위키)은 수동 회수, 각인은 자동 회수
- recall_count 가중치로 자주 회수되는 각인이 더 높은 우선순위
- 시간이 지날수록 시스템이 진화 (에이전트 실수 감소)
- 하네스 4기둥 중 "피드백 루프"의 구체적 구현

**결과**:
5개 파일 추가 (imprints.json, active-imprints.md, imprint-session-start.js, imprint-prompt-match.js, harness-imprint/SKILL.md). hooks.json의 SessionStart + UserPromptSubmit에 각인 훅 추가.

---

## ADR-005: 프롬프트 자동 정제 + 용어사전 자동 진화 + ToT 프레임워크

**상태**: 채택 (2026-04-07)

**컨텍스트**:
사용자가 비공식 표현("요약해줘", "대충")으로 프롬프트를 입력하면 에이전트가 의도를 부정확하게 해석할 수 있다. 용어사전이 존재하지만 수동으로만 갱신되어 활용도가 낮았다.

**결정**:
1. `prompt-refiner.js` (UserPromptSubmit 훅)로 용어사전 + 각인을 사용자 입력마다 자동 매칭
2. "요약" -> "발췌 정리" 등 고정 교정 맵 내장
3. 작업 완료 시 용어사전 자동 갱신 규칙을 CLAUDE.md에 명시
4. ToT(Tree-of-Thought) 4단계 프레임워크를 `prompt-rules.md`에 문서화
5. prompt-refiner.js가 기존 imprint-prompt-match.js를 흡수 (단일 훅으로 통합)

**근거**:
- 프롬프트 품질 = 응답 품질. 입력 단계에서 정제하면 출력 품질이 구조적으로 향상
- 용어사전이 사용할수록 풍부해지면 매칭 정확도 상승 (진화하는 시스템)
- ToT는 복잡한 문제에만 적용하여 단순 질문의 오버헤드 방지

**결과**:
prompt-refiner.js가 UserPromptSubmit에서 3가지를 동시 수행: (1)고정 교정, (2)용어사전 매칭, (3)각인 회수. 단일 훅으로 통합하여 타임아웃 3초 내 처리.

---

## ADR-006: Cross-Project Wiki (001_Wiki_AI) with Relative Path Bridge

**상태**: 채택 (2026-04-08)

**컨텍스트**:
지식(용어, 개념, 소스 분석)이 프로젝트 세션 로그에 흩어져 있어 누적/검색이 어렵다. Karpathy LLM Wiki 패턴을 적용하여 중앙 집중 지식 위키를 구축하되, 프로젝트 수명주기와 독립적으로 운영해야 한다.

**결정**:
001_Wiki_AI를 005_AI_Project의 형제 디렉토리(../001_Wiki_AI)로 배치. WIKI_ROOT = ../001_Wiki_AI 상대경로로 연결. pre-tool-guard.js에 형제 디렉토리 쓰기 허용 추가.

**근거**:
- 관심사 분리: 프로젝트 작업공간(005) vs 지식 기반(001)
- 위키는 프로젝트 수명주기를 초월 (지식 > 프로젝트)
- Obsidian Vault 호환성: 표준 마크다운 링크만 사용
- OneDrive 동기화: 상대경로만 사용하여 멀티PC 이식성 보장

**결과**:
- pre-tool-guard.js에 형제 디렉토리 허용 로직 추가 (IMP-005)
- CLAUDE.md에 WIKI_ROOT 경로 명시
- llm-wiki 스킬이 Tier-A로 등록 (scripts/ + Navigator.md)

---

## ADR-007: ECC(Everything Claude Code) 전체 통합

**상태**: 채택 (2026-04-10)

**컨텍스트**:
ECC v1.10.0(147K stars, 181 스킬, 47 에이전트, 33 훅 스크립트)을 Harness에 통합하여 범용 개발 자동화 기능을 확보하고자 함. 글로벌(~/.claude/)에 이미 설치 완료. 10/14 Hook 이벤트에서 충돌 발생.

**결정**:
ECC_HOOK_PROFILE=minimal로 충돌 훅 비활성화. ECC_DISABLED_HOOKS=session:start로 세션 초기화는 Harness 전용. settings.local.json에 env로 설정. deny 목록에 sudo/chmod 777/>/dev/ 추가.

**근거**:
- Harness 우선 원칙: 프로젝트 레벨이 글로벌 레벨보다 우선
- ECC minimal 프로필: 충돌 없는 유용한 훅만 생존 (block-no-verify, auto-tmux, command-log, session-end, evaluate-session, cost-tracker)
- 스킬/에이전트/규칙은 글로벌 레벨에서 자동 공존 (프로젝트 섀도잉으로 충돌 해결)

**결과**:
- 005에서 ECC 181 스킬 + 47 에이전트 + 89 규칙 사용 가능
- Harness 모든 기능(각인, pre-tool-guard, post-tool-validate, prompt-refiner, PDCA, Wiki) 그대로 유지
- AgentShield 보안 스캐너 npx로 실행 가능

---

## ADR-008: SYSTEM_NAVIGATOR.md 도입

**상태**: 채택 (2026-04-10)

**컨텍스트**:
시스템 복잡도 증가(28개 스킬, 12개 각인, 15개 훅 이벤트, 9개 MCP, 9개 지원문서)로 전체 구조 파악이 어려워짐. 하네스/bkit/스킬 3계층의 관계와 각 컴포넌트의 동기/동작방식을 문서화할 필요 발생.

**결정**:
프로젝트 루트에 SYSTEM_NAVIGATOR.md를 배치. Mermaid 체계도+흐름도로 시스템 전체를 시각화. navigator-updater.js PostToolUse 훅으로 핵심 파일 변경 시 자동 갱신. AUTO 마커 기반 섹션 교체 방식.

**근거**:
- CLAUDE.md(70줄)은 규칙 정의용이지 시스템 구조 문서화용이 아님
- 9개 지원문서는 각각의 도메인을 다루지만 전체 그림을 보여주지 못함
- 비작동 구간(Gap) 식별과 추적이 필요
- harness-architect 7단계 프로세스를 통해 구조적으로 생성

**결과**:
- pre-tool-guard.js 허용 목록에 system_navigator.md 추가
- governance-rules.md 루트 구조 테이블에 SYSTEM_NAVIGATOR.md 행 추가
- navigator-updater.js PostToolUse 훅으로 자동 갱신
- CLAUDE.md 참조 문서에 시스템 네비게이터 추가

---

## ADR-009: 브랜치 분리 전략 -- system/* vs feat/*

**상태**: 채택 (2026-04-15)

**컨텍스트**:
단일 master 브랜치에 시스템 인프라(.claude/, .harness/, .bkit/, .agents/skills/, root CLAUDE.md)와 프로젝트 작업(Projects/*)을 혼합 커밋하면, 변경 이력 추적과 롤백이 어렵다. 특히 하네스 훅/스킬 변경이 프로젝트 코드에 영향을 주는 경우 원인 분리가 불가능하다.

**결정**:
커밋 시 시스템 변경과 프로젝트 변경을 별도 브랜치로 분리한다.

| 브랜치 패턴 | 범위 | 포함 경로 |
|------------|------|-----------|
| `master` | 안정 통합 | merge만 |
| `system/*` | 하네스/bkit/스킬 인프라 | `.claude/`, `.harness/`, `.bkit/`, `.agents/`, root `CLAUDE.md`, `adr.md` |
| `feat/*` | 프로젝트 작업 | `Projects/`, `.gitignore`, `Output/` |

**근거**:
- 시스템 훅 변경이 프로젝트 코드를 깨뜨릴 때 즉시 식별 가능
- 프로젝트 추가/제거가 하네스 이력을 오염시키지 않음
- 하네스 4기둥 중 기둥2(CI/CD): 시스템 변경과 비즈니스 변경의 관심사 분리

**결과**:
2026-04-15 첫 적용. `system/harness-evolution` + `feat/projects` 브랜치 생성.

---

## ADR-010: .gitignore 생성파일 제외 정책

**상태**: 채택 (2026-04-15)

**컨텍스트**:
`.bkit/runtime/`, `.bkit/snapshots/`, `HarnessWorkspace/`, `.harness/tmp_refine/`, `**/.bkit_runtime/` 등 런타임 생성 디렉토리가 git에 추적되어 VS Code Source Control에 10,000+ 변경이 표시됨. OneDrive 동기화와 결합하여 파일 감시 이벤트가 폭증.

**결정**:
런타임/캐시/생성 파일은 `.gitignore`에서 구조적으로 제외한다.

| 제외 경로 | 근거 |
|-----------|------|
| `HarnessWorkspace/` | 하네스 작업 임시 공간 |
| `.bkit/runtime/`, `.bkit/snapshots/` | bkit 런타임 상태 |
| `.harness/ingest-cache.json`, `.harness/refine-log.jsonl`, `.harness/tmp_refine/` | 하네스 캐시/임시 |
| `**/.bkit_runtime/` | 프로젝트별 생성 데이터 (json, png, mmd) |
| `/Output/` | 루트 레벨 산출물 |
| `**/input/Question/` | 사용자 질문 스크린샷 |

**근거**:
- 생성 파일은 재생성 가능. git 추적은 저장소 비대화만 유발
- OneDrive 동기화 환경에서 생성 파일 추적은 VS Code 성능 저하 원인
- 하네스 4기둥 중 기둥3(도구경계): 추적 대상을 소스코드+설정으로 한정

**결과**:
root `.gitignore`에 13줄 추가. VS Code Source Control 변경 수 10,000+ -> 7건으로 감소.
