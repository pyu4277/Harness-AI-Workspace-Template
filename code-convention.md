# 코딩 규칙 (Code Convention)

> 005_AI_Project의 코드 작성 표준.
> CLAUDE.md에서 참조됨. 에이전트와 사람 모두 준수.

---

## 네이밍 규칙

| 대상 | 스타일 | 예시 |
|:---|:---|:---|
| Python 변수/함수 | snake_case | `file_path`, `extract_text()` |
| Python 클래스 | PascalCase | `DocumentParser` |
| Python 상수 | UPPER_SNAKE | `MAX_RETRIES` |
| JavaScript 변수/함수 | camelCase | `fileName`, `parseInput()` |
| JavaScript 클래스 | PascalCase | `PhaseTracker` |
| 파일명 (코드) | kebab-case 또는 snake_case | `pre-tool-guard.sh`, `handoff.py` |
| 파일명 (산출물) | YYMMDD_이름_태그 | `260401_기획처_보고서_Final` |

## 인코딩

| 파일 유형 | 인코딩 | 명시 방법 |
|:---|:---|:---|
| HWP/CSV (레거시) | cp949 | `open(f, encoding='cp949')` |
| 그 외 모든 파일 | UTF-8 | 기본값 (명시 불필요) |

## 경로 처리

- 절대경로 하드코딩 금지 (PostToolUse 훅이 차단)
- 상대경로 사용: `./docs/support/...`
- Python 동적 경로: `Path(__file__).resolve().parents[N]` 또는 `Path(os.getcwd())`
- 공백 포함 경로: 항상 따옴표 처리

## 주석/문서 언어

- 코드 주석: 한국어 (기술 용어는 영어 유지)
- 변수명/함수명: 영어
- 마크다운 문서: 한국어
- 커밋 메시지: 한국어 또는 영어 (프로젝트별 통일)

## Python 스타일

- 타입 힌트 권장 (복잡한 함수에 한정, 모든 곳에 강제하지 않음)
- docstring: 공개 함수/클래스에만 (간결하게)
- subprocess 사용 시 `errors="replace"` 필수
- `try/except`에서 bare except 금지 -- 구체적 예외 지정

## JavaScript/Node.js 스타일

- `const` 우선, `let` 필요 시만
- `var` 사용 금지
- async/await 우선 (콜백 지양)
- `require()` 대신 `import` 사용 가능 (ESM 지원 시)

## 금지 패턴 (PostToolUse 훅이 구조적 차단)

- `eval()`, `new Function()`, `document.write()`
- 하드코딩된 시크릿 (`api_key = "..."` 등)
- 이모티콘 유니코드
- 절대경로 (`C:\Users\...`, `/home/...`)
