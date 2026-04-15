# 260414_Student_Admission_AI

학생 객관 자료 기반 기업 맞춤 자소서/이력서/포트폴리오를 회차 반복으로 합격까지 개선하는 시스템. 3층 엔지니어링(프롬프트+컨텍스트+하네스) 적용.

## 핵심 규칙

- 응답은 한국어. 코드/경로/변수는 영어 유지.
- 파일명: `YYMMDD_[이름]_[태그]` (리서치/로그), 출력은 고정명(`자소서.md`, `이력서.md`, `포트폴리오.md`).
- 회차 작업은 `round_N/` 안에서만. 이전 회차(round_M, M<N) 수정 금지.
- 모든 수치·성과·기업 주장은 `evidence_vault/` 또는 `research_cache/round_N/`에 인용 링크 필수.
- 에이전트 분리: writer ≠ reviewer (반드시 다른 세션). 리뷰 반영은 writer 세션에서.
- 리서치는 researcher 에이전트 전용. writer/ideator는 MCP 호출 금지.
- 학생 PII(이름·생년월일·학번·연락처)는 외부 MCP에 전달 금지.
- 회차 생성 시 `common/templates/round_skeleton/` 복제 + 이전 CHANGELOG의 "구조 개선" 항목 반영.
- 2차 회차부터 `round_N/CHANGELOG.md` 필수 (개선 가설/구조 변경/품질 변화).
- 문서 생성 시 Mermaid 흐름도 + 예시 포함.

## 절대 금지

- 학생 경력/자격/수치 **창작** (evidence_vault/ 외 사실 생성 금지).
- 타인 합격 자소서 **문장 복제** (구조·프레임만 학습).
- evidence_vault/ **수정·삭제** (등록 후 불변).
- 이전 회차 폴더 **수정·삭제** (회차 불변성).
- 금지 표현 사용: "최고의", "완벽한", "업계 1위" (근거 없이), "모든", "항상", 자기비하(`~에 불과`, `감히`).
- `.env`/credentials/API Key 하드코딩, 노출, 커밋.
- PII를 WebSearch/Exa/firecrawl 파라미터에 포함.
- 이모티콘 사용 (PostToolUse 훅 차단).
- 절대경로 하드코딩 (PostToolUse 훅 차단).
- `rm -rf`, `git push --force`, `git reset --hard`.

## 회차 작업 순서 (UC-02)

1. `/round new` → round_N/ 생성
2. input/{company_form.md, job_description.md, meta.json} 사용자 투입
3. researcher → research_cache/round_N/ 4종
4. writer → company_profile.md (D+3 템플릿)
5. ideator → ideas.md 3+
6. writer → output/ 3종 초안
7. /clear → 새 세션에서 reviewer
8. 수정 루프 → 사용자 승인 → CHANGELOG(N≥2)

## 참조 문서

- 설계문서: `docs/D1_domain-glossary.md` ~ `docs/DP3_company-profile-template.md` (12종)
- 코딩/작문 표준: `docs/D5_dev-standard.md`
- 회차 운영: `docs/DP1_round-operation.md`
- 리서치 규약: `docs/DP2_research-pipeline.md`
- 아키텍처: `docs/D4_architecture.md`
- 아키텍처 결정 기록: `adr.md`
- 코드 규약: `code-convention.md`

## 에이전트 운영

- 실수 발생 시 이 파일에 규칙 1줄 추가(자기 진화) + adr.md에 WHY 기록.
- 구현 완료 후 컨텍스트 40% 이하 유지. 초과 시 /clear.
- 회차 종료 시 CHANGELOG.md에 품질 변화 + 프롬프트 개선점 기록.
