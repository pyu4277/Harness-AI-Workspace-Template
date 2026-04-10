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
- 문서 시각화: 스킬/워크플로우/파이프라인/설계문서/지침서 생성 시 Mermaid 흐름도 + 예시 3개 필수. 버그 수정/설정 변경/1회성 스크립트는 미적용
- 핵심 용어 동의어: 지침 = 기능 = 워크플로우 = 파이프라인
- 존재하지 않는 스킬/MCP/스크립트 지어내기 금지
- 50페이지 이상 PDF 분석 시 `.txt` 사전 추출 후 시작 (AER-003)
- Wiki 지식베이스: `WIKI_ROOT = ../001_Wiki_AI` (PROJECT_ROOT 기준 상대경로). 위키 연동 시 llm-wiki 스킬 사용 (IMP-005)
- 계획/설계 단계 진입 시 `docs/support/design-documents.md` 28종에서 필요 문서만 선별 후 사용자 승인

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
- 설계문서 카탈로그: `./docs/support/design-documents.md` (28종 조건부 선택)
- 프롬프트 규칙: `./docs/support/prompt-rules.md` (ToT + 응답 규칙)
- 용어사전: `./docs/LogManagement/용어사전.md`
- ECC 통합: ECC_HOOK_PROFILE=minimal, ECC_DISABLED_HOOKS=session:start (하네스 우선, ADR-007)

## 에이전트 운영

- 실수 발생 시 이 파일에 규칙 1줄 추가 (자기 진화 메커니즘)
- 작업 중 고투/에러/재시도 발생 시 `/imprint record`로 각인 기록 (진화하는 학습)
- 작업 완료 시 대화에서 전문용어 대체 가능한 표현 발견하면 용어사전 자동 등록
- 사용자 프롬프트에서 장황한 설명이 용어사전의 전문용어로 압축 가능하면 내부 치환하여 정확히 이해 (의미 불변 원칙)
- "요약" 요청은 "발췌 정리"로 내부 해석 (원문 기반 추출, 환각 방지)
- 분석/기획/설계/비교/의사결정 요청 시 ToT 4단계 자동 적용. 단순 질문/파일 작업은 즉시 처리 (prompt-rules.md 참조)
- 코드 작성과 코드 리뷰는 반드시 다른 에이전트
- 구현 완료 후 컨텍스트 사용량 40% 이하 유지 권장
- /harness-architect 호출 시 SKILL.md Phase 1~7 전체를 반드시 순서대로 실행. Phase 건너뛰기 금지 (2026-04-10 실수 기반 추가)
- 계획/설계/개발 요청 시 SKILL.md에 정의된 프로세스가 있으면 그 프로세스를 100% 따른다. 임의 단축 금지 (2026-04-10 실수 기반 추가)

## 완료 체크리스트 (구조적 강제 -- prompt-refiner.js가 자동 주입)

모든 다단계 작업 완료 시 반드시 아래를 출력한다. prompt-refiner.js 훅이 작업성 프롬프트에 이 체크리스트를 자동 주입하므로, 누락 시 하네스 위반이다.

1. **Feature Usage 요약**: Used (사용한 도구/스킬), Not Used (미사용 도구), Recommended (후속 작업)
2. **전문용어 등록**: 세션 중 발견한 전문용어 -> term-organizer로 용어사전 등록
3. **에러 각인**: 에러/재시도/번거로운 작업 -> `/imprint record`로 각인 등록
4. **프롬프트 정제**: 사용자 프롬프트가 모호하면 개선된 버전을 먼저 제시 후 승인받고 진행
