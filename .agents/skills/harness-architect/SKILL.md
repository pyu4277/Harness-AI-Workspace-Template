---
name: harness-architect
classification: workflow
classification-reason: "7단계 파이프라인 오케스트레이션, 모델 독립적 가치"
deprecation-risk: none
description: |
  새 프로젝트에 하네스 엔지니어링 4기둥 원칙을 자동 적용하는 워크플로우.
  프로젝트 분석 → 설계문서 선택 → 문서 생성 → CLAUDE.md/훅/권한 설계 → 검증 → 설치.

  Use proactively when:
  - 사용자가 새 프로젝트를 시작할 때
  - "프로젝트 세팅", "CLAUDE.md 만들어줘", "하네스 적용" 요청 시
  - "project init", "project setup" 요청 시

  Triggers: harness, 하네스, project init, 프로젝트 초기화, 프로젝트 세팅,
  CLAUDE.md 생성, 규칙 만들기, project setup, 프로젝트 시작, 하네스 아키텍트,
  harness architect, harness engineering, 하네스 엔지니어링

  Do NOT use for: 기존 프로젝트 코드 구현, 단순 파일 편집, 버그 수정,
  이미 하네스가 구성된 프로젝트의 일반 작업
argument-hint: "init [프로젝트명]"
user-invocable: true
---

# Harness Architect — 하네스 엔지니어링 프로젝트 초기화 워크플로우

> 새 프로젝트에 하네스 엔지니어링 4기둥 원칙을 자동 적용한다.
> 모든 결정 지점에서 사용자 승인을 받는다 (Decision Gate).
> 출처: Mitchell Hashimoto, Martin Fowler, 4개 영상 154분 분석 기반.

## 사전 준비
이 스킬을 실행하기 전에 반드시 `knowledge/harness-engineering-guide.md`를 읽어 4기둥 원칙을 완전히 이해한다.

## 실행 방법
```
/harness-architect init [프로젝트명]
```

---

## Phase 1: 프로젝트 인터뷰 및 분석

### 목표
프로젝트의 유형, 규모, 기술스택을 파악하여 프로파일 JSON을 생성한다.

### 1-1. 기존 코드 자동 분석 (코드가 있는 경우)
- `Glob`으로 프로젝트 파일 구조 탐색
- `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml` 등 의존성 파일 확인
- 기존 `CLAUDE.md` 존재 여부 확인
- `.env` 패턴으로 환경변수 구조 파악
- 기존 `.claude/` 디렉토리 구조 확인

### 1-2. 사용자 인터뷰 (필수 — 스킵 불가)
반드시 `AskUserQuestion`으로 아래 정보를 수집한다.

**필수 질문 5개:**
1. "이 프로젝트는 무엇을 만드는 건가요? (한 줄 설명)"
2. "주요 기술스택이 무엇인가요? (언어, 프레임워크)"
3. "데이터베이스를 사용하나요? (종류)"
4. "API가 있나요? (REST/GraphQL/없음)"
5. "UI가 있나요? (웹/모바일/CLI/없음)"

**선택 질문 (규모 판단):**
6. "팀 규모는? (1인/2-5명/6명 이상)"
7. "마이크로서비스 구조인가요?"
8. "예상 개발 기간은?"

### 1-3. 프로파일 JSON 생성

```json
{
  "project_name": "string",
  "description": "string",
  "type": "web|api|fullstack|cli|library|mobile|data-pipeline",
  "scale": "starter|dynamic|enterprise",
  "tier": 1,
  "tech_stack": {
    "language": [],
    "framework": [],
    "database": null,
    "api_type": "none",
    "ui_type": "none"
  },
  "team_size": "solo",
  "has_existing_code": false,
  "has_existing_claude_md": false
}
```

### 1-4. Tier 자동 결정
- Tier 1 (Starter): 정적 웹, CLI 도구, 소규모 라이브러리
- Tier 2 (Dynamic): 풀스택 앱, API 서버, DB 사용 프로젝트
- Tier 3 (Enterprise): 마이크로서비스, 대규모 팀, 복잡한 인프라

### Decision Gate G1
```
"프로젝트 분석 결과입니다:
 - 유형: [type]
 - 규모: [scale] (Tier [tier])
 - 기술스택: [요약]
 이 분류가 맞습니까?"
```

---

## Phase 2: 설계문서 선택

### 3-Tier 선택 로직

#### Tier 1 — 모든 프로젝트 (필수 5종)
1. 사업 기획서 — 프로젝트의 WHY/WHAT/SCOPE
2. 요구사항 정의서 — 기능 범위 정의
3. 아키텍처 설계서 — 시스템 구조
4. 개발 표준 정의서 — 코딩 표준 포함
5. 도메인 정의서 + 용어사전 — 도메인 언어 통일

#### Tier 2 — Dynamic+ (조건부 추가 6종)
| 문서 | 선택 조건 |
|------|-----------|
| SRS | scale >= dynamic |
| 상세설계서 | scale >= dynamic |
| ERD | database != null |
| API 명세서 | api_type != none |
| 순서도 및 절차도 | 비즈니스 로직 복잡 |
| 인터페이스 설계서 | 외부 시스템 연동 |

#### Tier 3 — Enterprise (조건부 추가 10종)
| 문서 | 선택 조건 |
|------|-----------|
| 통합설계서 | 마이크로서비스 |
| 시스템 아키텍처 설계서 | scale = enterprise |
| 데이터베이스 설계서 | DB + scale >= dynamic |
| 테이블/컬럼 정의서 | DB + scale = enterprise |
| 요구사항 추적서 | team_size >= medium |
| 체계도 | scale = enterprise |
| 프로그램 목록 | 모듈 수 >= 10 |
| 산출물 적용 계획표 | team >= small + scale >= dynamic |
| 타당성 분석서 | scale = enterprise |
| 메뉴 구성도 | ui_type in {web, mobile} |

### 생성 순서 (의존성 기반)
1. 도메인 정의서 + 용어사전 (용어 기반)
2. 사업 기획서 (스코프)
3. 요구사항 정의서 (기능)
4. 아키텍처 설계서 (구조)
5. 개발 표준 정의서 (규칙)
6. 나머지 (의존성 순)

### Decision Gate G2
```
"이 프로젝트에 필요한 문서 [N]종을 선택했습니다:
 [목록 + 선택 근거]
 추가/제거할 문서가 있습니까?"
```

---

## Phase 3: 설계문서 생성

### 모든 문서 공통 — 4기둥 반영
각 문서 상단에 포함:

```markdown
## 하네스 엔지니어링 적용
| 기둥 | 이 문서에서의 역할 |
|------|-------------------|
| 기둥1 (컨텍스트) | [CLAUDE.md 반영 방법] |
| 기둥2 (CI/CD) | [자동 검증 요구사항] |
| 기둥3 (도구경계) | [접근 제한 사항] |
| 기둥4 (피드백) | [위반 감지/수정 방안] |
```

### 문서별 핵심

**사업 기획서**: 개요, 목표, 범위(IN/OUT), 이해관계자, 리스크, 하네스 적용 계획
**요구사항 정의서**: FR-XXX + "검증 방법" 컬럼, NFR-XXX + "위반 시 대응" 컬럼
**아키텍처 설계서**: 계층 구조, 의존성 규칙, 보안 경계, 아키텍처 테스트 명세
**개발 표준 정의서**: 네이밍, 린터, 금지 패턴, PR규칙, 에이전트 규칙(컨텍스트 40%)
**도메인+용어사전**: 개념 정의, 한영 병기, 약어, 관계도

### 출력 위치
프로젝트 `docs/` 폴더. 각 문서 생성 후 TodoWrite 갱신.

---

## Phase 4: 하네스 설계

### 4-1. CLAUDE.md 생성 (60줄 이하 엄수)
규칙 추출: 요구사항→핵심규칙, 아키텍처→절대금지, 개발표준→code-convention.md로 분리

### 4-2. settings.local.json 생성
permissions (allow/deny) + hooks (PreToolUse, PostToolUse)

### 4-3. 훅 스크립트 생성
- `pre_tool_guard.sh` — 허용 경로만 쓰기
- `post_tool_validate.sh` — 금지 패턴 감지

### 4-4. 지원 문서 생성
- `code-convention.md`, `adr.md`

### Decision Gate G3: CLAUDE.md 승인
### Decision Gate G4: 보안 설정 승인

---

## Phase 5: 4기둥 검증 (100점 만점)

기둥1 컨텍스트(25) + 기둥2 CI/CD(25) + 기둥3 도구경계(25) + 기둥4 피드백(25)
합격: >= 90점 → Phase 7 | 불합격: < 90점 → Phase 6

---

## Phase 6: 자동 개선 (불합격 시, 최대 3회)

---

## Phase 7: 설치 + 보고

### Decision Gate G5: 설치 승인
설치 대상: CLAUDE.md, .claude/settings.local.json, .claude/hooks/*, code-convention.md, adr.md, docs/*

### 설치 시 기존 파일 백업 (.bak)

---

## 하네스 4기둥 요약

| 기둥 | 정의 | Claude Code 구현체 |
|------|------|-------------------|
| 1. 컨텍스트 파일 | 세션 자동 로드 설정 | CLAUDE.md (60줄 이하) |
| 2. CI/CD 게이트 | 위반 구조적 차단 | hooks (Pre/PostToolUse) |
| 3. 도구 경계 | 최소 권한 물리 적용 | permissions (allow/deny) |
| 4. 피드백 루프 | 자기 진화 메커니즘 | 실수→규칙추가 루프 |

**최상위 규칙**: 실수하면 프롬프트가 아닌 하네스를 고쳐라.
