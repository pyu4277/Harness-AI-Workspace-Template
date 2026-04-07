# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## 응답 규칙
- 응답은 항상 한국어로
- 코드 주석은 한국어로 (변수명/함수명은 영어)

## 핵심 규칙
{{CORE_RULES}}

## 절대 금지 (Hard Rules — 구조적 강제)
{{PROHIBITIONS}}

## 참조 문서
- 코딩 규칙: ./code-convention.md
- 아키텍처 결정: ./adr.md
{{ADDITIONAL_REFERENCES}}

## 에이전트 운영 규칙
- 실수 발생 시 이 파일에 규칙 1줄 추가 → 동일 실수 구조적 재발 방지
- 규칙 추가 시 반드시 사용자 승인 후 추가
- 컨텍스트 소모 40% 이하 유지 목표
- QA/브라우저 테스트는 서브에이전트로 분리
