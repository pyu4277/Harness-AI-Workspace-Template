# Harness AI Workspace Template

> Claude Code + bkit v1.6.2 + Harness Engineering 4-Pillar.
> AI 에이전트의 실수를 프롬프트가 아닌 **구조**로 방지하는 작업 공간 템플릿.

---

## 이게 뭔가요?

AI 코딩 에이전트에게 "이거 하지 마" 라고 말하는 것은 **부탁**입니다. 무시할 수 있습니다.
이 템플릿은 "하지 마"를 **구조적으로 불가능**하게 만듭니다.

| | 프롬프트 (부탁) | 하네스 (강제) |
|---|---|---|
| 이모티콘 금지 | CLAUDE.md에 "쓰지 마" | PostToolUse 훅이 유니코드 감지 후 차단 |
| 절대경로 금지 | CLAUDE.md에 "쓰지 마" | PostToolUse 훅이 패턴 감지 후 차단 |
| 설정 파일 보호 | CLAUDE.md에 "건드리지 마" | PreToolUse 훅이 경로 검사 후 차단 |
| rm -rf 금지 | CLAUDE.md에 "실행하지 마" | settings.local.json deny 목록으로 차단 |

## 핵심 구조: 3계층 분리

```
[하네스 계층] 거버넌스 -- 무엇이 금지인지 강제
  CLAUDE.md (46줄)         선언
  .claude/hooks/*.js       구조적 차단
  settings.local.json      명령어 차단

[bkit 계층] 워크플로우 -- 어떤 순서로 할지 안내
  bkit.config.json         PDCA 설정
  .bkit/plugin/            라이프사이클 훅 + 라이브러리

[스킬 계층] 도메인 기능 -- 무엇을 할 수 있는지 정의
  .agents/skills/          21개 도메인 스킬
  .agents/agents/          31개 에이전트 정의
  .agents/templates/       PDCA 문서 템플릿
```

## 하네스 4기둥

| 기둥 | 정의 | 구현체 |
|------|------|--------|
| 1. 컨텍스트 | 매 세션 자동 로드 | CLAUDE.md (60줄 이하) + 지원 문서 7개 |
| 2. CI/CD 게이트 | 위반 구조적 차단 | PreToolUse/PostToolUse 훅 (Node.js) |
| 3. 도구 경계 | 최소 권한 물리 적용 | permissions deny 목록 |
| 4. 피드백 루프 | 자기 진화 메커니즘 | 실수 -> 규칙 추가 루프 |

## 빠른 시작

```bash
# 1. 클론
git clone https://github.com/YOUR_USERNAME/Harness-AI-Workspace-Template.git my-project
cd my-project

# 2. Claude Code 실행
claude

# 3. 하네스가 자동으로 작동합니다
#    - 이모티콘 쓰면 차단
#    - 절대경로 쓰면 차단
#    - .env 건드리면 차단
#    - rm -rf 실행하면 차단
```

## 포함된 스킬 (29개)

### 도메인 스킬

| 스킬 | 용도 |
|---|---|
| HWPX_Master | 한글 문서(.hwpx) 생성/수정/추출/자동화 |
| DocKit | PDF/DOCX/PPTX 처리 |
| PaperResearch | RISS + Google Scholar 학술 검색 |
| VisualCapture | 화면 캡처 + Vision 분석 |
| PromptKit | 프롬프트 엔지니어링 4단계 |
| Mermaid_FlowChart | ELK 렌더러 Mermaid 흐름도 |
| FileNameMaking | 시맨틱 평가 기반 파일명 변경 |
| mdGuide | 마크다운 품질 검증 |
| term-organizer | 용어사전 관리 |
| session-handoff | 세션 지식 증류 + 로그 |
| auto-error-recovery | 자동 에러 분석/복구 |
| ServiceMaker | 9단계 스킬 개발 |
| harness-architect | 하네스 엔지니어링 프로젝트 초기화 |

### bkit 프레임워크 스킬

| 스킬 | 용도 |
|---|---|
| pdca | PDCA 전체 주기 (PM/Plan/Design/Do/Check/Act/Report) |
| plan-plus | 브레인스토밍 강화 기획 |
| development-pipeline | 9단계 개발 파이프라인 |
| code-review | 코드 품질 분석 |
| zero-script-qa | Docker 로그 기반 QA |
| btw | 개선 제안 수집 |
| bkit-rules | 코어 규칙 (레벨 감지, 자동 트리거) |
| bkit-templates | PDCA 문서 템플릿 |

## 프로젝트 구조

```
Harness-AI-Workspace-Template/
  CLAUDE.md              거버넌스 (46줄)
  code-convention.md     코딩 규칙
  adr.md                 아키텍처 결정 기록
  .claude/hooks/         하네스 가드 (Node.js)
  .agents/               스킬 + 에이전트 + 템플릿
  .bkit/                 bkit 런타임
  Projects/_TEMPLATE/    새 프로젝트 템플릿
  docs/support/          지원 문서 7개
```

## 커스터마이징

1. **CLAUDE.md** 수정: 프로젝트에 맞는 규칙 추가 (60줄 이하 유지)
2. **code-convention.md** 수정: 팀 코딩 스타일에 맞게
3. **adr.md** 추가: 새 아키텍처 결정 시 ADR-NNN 추가
4. **.claude/hooks/*.js** 수정: 금지 패턴/허용 경로 커스터마이징
5. **settings.local.json** 수정: deny 목록 조정

## 요구 사항

- Windows 11
- Node.js v20+
- Claude Code

## 라이선스

MIT

## 출처

하네스 엔지니어링 4기둥 원칙: Mitchell Hashimoto (2026.02), Martin Fowler
bkit 프레임워크: bkit v1.6.2
