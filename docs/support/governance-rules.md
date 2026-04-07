# 거버넌스 규칙 상세

> CLAUDE.md에서 분리된 거버넌스 규칙의 전체 내용.
> 하네스 4기둥에 의해 구조적으로 강제되는 규칙은 [HARNESS] 태그로 표시.

---

## 1. 이모티콘 사용 금지 [HARNESS]

**강제 방식**: PostToolUse 훅 (`post-tool-validate.sh`)이 유니코드 이모티콘 범위를 감지하여 Write/Edit를 차단한다.

AI가 생성, 작성, 수정하는 모든 결과물(기술문서, 지침서, 스크립트, 프롬프트, 분석 보고서 등)에서 이모티콘(Emoji, Emoticon) 및 불필요한 특수기호 사용을 금지한다.

- 마크다운 문법(Heading, Bold, List, Table)만으로 가독성을 확보한다
- 기존 파일에 이모티콘이 있더라도 새로 작성하는 결과물에는 포함하지 않는다

## 2. 절대경로 하드코딩 금지 [HARNESS]

**강제 방식**: PostToolUse 훅이 `[A-Z]:\`, `/Users/`, `/home/` 패턴을 감지하여 차단한다.

이 프로젝트는 OneDrive를 통해 여러 PC에서 접근하므로 절대경로를 어떤 파일에도 하드코딩하지 않는다.

- 모든 경로는 `${PROJECT_ROOT}` 기준 상대경로로 작성
- `${PROJECT_ROOT}` = CLAUDE.md가 위치한 폴더
- Python 스크립트: `Path(os.getcwd())` 또는 `Path(__file__).resolve().parents[N]`
- 어떤 PC에서 실행하더라도 즉시 동작하는 이식성(Portability) 확보

## 3. 루트 구조 잠금 [HARNESS]

**강제 방식**: PreToolUse 훅 (`pre-tool-guard.sh`)이 허용 경로 외 Write/Edit를 차단한다.

최상위 폴더(`005_AI_Project/`) 구조는 아래 목록으로 고정:

| 항목 | 유형 | 설명 |
|:---|:---:|:---|
| `CLAUDE.md` | 파일 | 루트 거버넌스 |
| `code-convention.md` | 파일 | 코딩 규칙 |
| `adr.md` | 파일 | 아키텍처 결정 기록 |
| `bkit.config.json` | 파일 | bkit 자동화 설정 |
| `.gitignore` | 파일 | Git 제외 목록 |
| `requirements.txt` | 파일 | Python 의존성 |
| `.claude/` | 폴더 | CC 설정 + 하네스 훅 |
| `.agents/` | 폴더 | 스킬 및 에이전트 |
| `.bkit/` | 폴더 | bkit 런타임 상태 |
| `Projects/` | 폴더 | YYMMDD_이름 형식 프로젝트 |
| `docs/` | 폴더 | 지원 문서 + PDCA 문서 + 세션 로그 |
| `Temporary Storage/` | 폴더 | 임시 파일 전용 |

위 목록에 없는 파일/폴더는 루트에 직접 생성 금지. 불명확한 경우 `Temporary Storage/`에 임시 저장.

## 4. 흐름도 + 예시 의무화

프로젝트, 기능, 스킬, MCP, 워크플로우, 지침 등 무엇을 새로 만들거나 변경하든 반드시:

1. **Mermaid FlowChart**: ELK 렌더러 기반 흐름도 생성. 분기 조건, 에러 경로, 출력 결과 모두 노드로 표현.
2. **다중 상황 예시**: 최소 3개 이상. 실제 맥락(학술, 행정, 보고서 등) 사용. 에러/경계 조건 시나리오 필수.

| 대상 | 흐름도 | 예시 |
|:---|:---:|:---:|
| 새 스킬 Tier-A | Navigator.md 필수 | Navigator.md 포함 |
| 새 스킬 Tier-B | SKILL.md 인라인 | SKILL.md 인라인 |
| 새 프로젝트 기획 | CLAUDE.md 또는 별도 파일 | 사용 시나리오 섹션 |
| MCP 서버 등록 | 트리거 테이블 하단 | 예시 명령어 3개 이상 |
| 워크플로우 변경 | 변경된 흐름도 업데이트 | 영향받는 예시 갱신 |

## 5. 핵심 용어 동의어

사용자가 아래 중 하나를 언급하면 나머지 3개를 모두 포함하는 의미로 해석:
- "지침" = 기능 = 워크플로우 = 파이프라인

## 6. 환각 금지 / 기존 자산 한정 사용

- 존재하지 않는 스킬, MCP, 스크립트, 기능을 지어내거나 임의로 호출하지 않는다
- 불확실한 정보는 "Data Missing"으로 명시하고 파일을 직접 확인
- 오직 `.agents/skills/`에 등록된 스킬과 실제 설치된 MCP 서버만 사용

## 7. 파일 관리 규칙

### 명명 규칙
- 프로젝트 폴더: `YYMMDD_[이름]` (예: `260401_EvaluatorV6`)
- 산출물: `YYMMDD_[담당]_[내용]_[태그]` (예: `260401_기획처_성과관리_Final`)
- 세션 로그: `session_YYMMDD_HHMM.md` (handoff.py 자동 생성)
- 임시 파일: `Temporary Storage/`에만 저장

### 파일 유형별 저장 위치

| 파일 유형 | 저장 위치 |
|:---|:---|
| 새 프로젝트 작업물 | `Projects/YYMMDD_이름/` |
| 산출물 | `Projects/YYMMDD_이름/Output/` |
| 입력 원본 | `Projects/YYMMDD_이름/Input/` |
| 소스 코드/스크립트 | `Projects/YYMMDD_이름/src/` 또는 `.agents/skills/[스킬명]/scripts/` |
| PDCA 기획/설계 문서 | `docs/01-plan/`, `docs/02-design/` 등 |
| 세션 로그 | `Projects/[프로젝트]/Log/` |
| 임시/테스트 파일 | `Temporary Storage/` |

## 8. AER 재발 방지 규칙

`auto-error-recovery` 세션에서 도출된 전역 적용 규칙:

| 규칙 ID | 내용 |
|:---|:---|
| AER-001 | 외부 API 호출 파이프라인 실행 전 API Key, 네트워크, 모델 가용성 사전 점검 |
| AER-002 | Phase 0에서 최종 산출물 형식 사용자에게 명시적 확인 |
| AER-003 | 50페이지 이상 PDF 분석 시 `.txt`로 사전 추출 후 분석 |
| AER-004 | 파일 편집 전 반드시 Read로 실제 내용 확인 [CLAUDE.md에도 기재] |
| AER-005 | Windows subprocess 사용 시 `errors="replace"` 옵션 [CLAUDE.md에도 기재] |
