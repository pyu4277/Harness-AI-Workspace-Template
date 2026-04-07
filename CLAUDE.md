# 005_AI_Project -- 순천대학교 연구/행정 자동화 플랫폼

> bkit v1.6.2 + 하네스 엔지니어링 4기둥 기반. 한국 대학 연구/행정 특화.
> 하네스 = 프롬프트(부탁)가 아닌 구조적 강제. 실수하면 하네스를 고쳐라.

## 핵심 규칙

- 응답/보고서/로그는 한국어. 코드/경로/변수는 영어 유지
- 파일명: `YYMMDD_[이름]_[태그]` (예: `260401_졸업논문_Draft`)
- 불확실하면 파일 확인 먼저, 없으면 사용자에게 질문 (No Guessing)
- 자동화 우선: PDCA 자동 적용, 반복 작업은 스크립트
- Script Before Edit: Python 스크립트로 해결 가능하면 직접 파일 편집 지양
- 편집 전 반드시 Read로 실제 내용 확인 (AER-004)
- subprocess 사용 시 `errors="replace"` 필수 (AER-005)
- 새 기능/스킬/워크플로우 생성 시 Mermaid 흐름도 + 3개 예시 필수
- 핵심 용어 동의어: 지침 = 기능 = 워크플로우 = 파이프라인
- 존재하지 않는 스킬/MCP/스크립트 지어내기 금지
- 50페이지 이상 PDF 분석 시 `.txt` 사전 추출 후 시작 (AER-003)

## 절대 금지

- 이모티콘 사용 (PostToolUse 훅이 구조적으로 차단)
- 절대경로 하드코딩 (PostToolUse 훅이 구조적으로 차단)
- 루트 구조 무단 변경 (PreToolUse 훅이 구조적으로 차단)
- `.env` 파일 내용 노출/커밋
- `eval()`, `new Function()` 사용
- 프로덕션 데이터 직접 삭제
- API Key 하드코딩 (반드시 `.env` + `.gitignore`)

## 참조 문서

- 거버넌스 상세: `./docs/support/governance-rules.md`
- 스킬 목록/트리거: `./docs/support/skill-catalog.md`
- 프로젝트 구조: `./docs/support/project-structure.md`
- 기술 환경: `./docs/support/tech-stack.md`
- 세션 프로토콜: `./docs/support/session-protocol.md`
- 도메인 규칙: `./docs/support/domain-rules.md`
- 스킬 개발 가이드: `./docs/support/skill-development.md`
- 코딩 규칙: `./code-convention.md`
- 아키텍처 결정: `./adr.md`
- 활성 각인: `./.harness/active-imprints.md` (세션 시작 시 자동 갱신)

## 에이전트 운영

- 실수 발생 시 이 파일에 규칙 1줄 추가 (자기 진화 메커니즘)
- 작업 중 고투/에러/재시도 발생 시 `/imprint record`로 각인 기록 (진화하는 학습)
- 코드 작성과 코드 리뷰는 반드시 다른 에이전트
- 구현 완료 후 컨텍스트 사용량 40% 이하 유지 권장
