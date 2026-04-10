# 프로젝트 구조

> 005_AI_Project의 디렉토리 구조 및 표준 프로젝트 레이아웃.

---

## 루트 구조

```
005_AI_Project/
├── CLAUDE.md              루트 거버넌스 (60줄 이하)
├── code-convention.md     코딩 규칙
├── adr.md                 아키텍처 결정 기록
├── bkit.config.json       bkit 자동화 설정
├── .claude/
│   ├── settings.json      CC 허용 도구
│   ├── settings.local.json  권한 deny 목록
│   ├── hooks.json         하네스 + bkit 통합 훅
│   ├── hooks/             하네스 가드 스크립트
│   │   ├── pre-tool-guard.js        경로 차단 (기둥 3)
│   │   ├── post-tool-validate.js    금지 패턴 (기둥 2)
│   │   ├── prompt-refiner.js        프롬프트 정제 (기둥 4)
│   │   ├── imprint-session-start.js 각인 로드 (기둥 4)
│   │   ├── imprint-prompt-match.js  각인 매칭
│   │   └── navigator-updater.js     SYSTEM_NAVIGATOR 자동 갱신
│   └── commands/          슬래시 커맨드 정의
├── .agents/
│   ├── skills/            25개 스킬 디렉토리 (도메인 + bkit + 외부)
│   ├── agents/            에이전트 정의 31개
│   └── templates/         PDCA 문서 템플릿 21개
├── .bkit/
│   ├── plugin/            bkit v1.6.2 런타임
│   └── state/             PDCA 상태, 메모리
├── Projects/              YYMMDD_이름 형식 프로젝트
├── docs/
│   ├── support/           지원 문서 7개 (CLAUDE.md에서 분리)
│   ├── LogManagement/     세션 로그 대시보드
│   ├── 01-plan/           PDCA 계획 문서
│   ├── 02-design/         PDCA 설계 문서
│   ├── 03-analysis/       PDCA 분석 문서
│   ├── 04-report/         PDCA 보고서
│   └── archive/           아카이브
└── Temporary Storage/     임시 파일 전용
```

## 하네스 계층 구조 (3계층 분리)

```
[하네스 계층 -- 거버넌스 (구조적 강제)]
  CLAUDE.md (60줄)           무엇이 허용/금지인지 선언
  .claude/hooks/*.js         PreToolUse/PostToolUse 차단 (6개 스크립트)
  settings.local.json deny   명령어 차단

[bkit 계층 -- 워크플로우 (프로세스 가이던스)]
  bkit.config.json           PDCA 설정, 품질 게이트
  .bkit/plugin/scripts/*.js  PDCA 라이프사이클 훅
  .bkit/plugin/lib/*.js      공통 라이브러리
  .bkit/state/               PDCA 상태 추적

[스킬 계층 -- 도메인 기능 (실행 능력)]
  .agents/skills/            도메인 스킬
  .agents/agents/            에이전트 정의
  .agents/templates/         PDCA 문서 템플릿
```

## 프로젝트 표준 구조 (`Projects/YYMMDD_이름/`)

```
YYMMDD_ProjectName/
├── CLAUDE.md              프로젝트별 컨텍스트
├── requirements.txt       Python 의존성
├── .env                   API 키 (gitignore 필수)
├── Log/                   session_YYMMDD_HHMM.md
├── Input/
│   ├── raw/               미가공 원본
│   ├── data/              정형 데이터
│   ├── refs/              참고/기준 문서
│   └── captures/          화면 캡처
├── Output/
│   ├── draft/             초안
│   ├── final/             최종 확정본
│   └── archive/           구버전 보관
├── src/
│   ├── agents/            AI 파이프라인 스크립트
│   ├── utils/             공통 유틸리티
│   └── tests/             테스트 코드
└── docs/
    ├── plan/              기획/설계 노트
    └── notes/             회의록/메모
```

## 새 프로젝트 생성 절차

1. `Projects/_TEMPLATE/` 폴더를 `Projects/YYMMDD_이름/`으로 복사
2. 복사한 폴더의 `CLAUDE.md` 내 프로젝트 개요 작성
3. `.env` 파일 생성 + `.gitignore`에 반드시 포함
