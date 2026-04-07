# 기술 환경

> 005_AI_Project의 기술 스택 및 Windows 환경 주의사항.

---

## 기본 환경

| 항목 | 값 |
|---|---|
| OS | Windows 11 (win32) |
| Python | 3.x (venv 권장) |
| 핵심 라이브러리 | win32com, lxml, aiohttp, PyMuPDF, python-docx |
| HWP 자동화 | win32com.client (HWP OLE) -- 한글 5.0+ 설치 필요 |
| Node.js | npm/npx 사용 가능 |
| 인코딩 | cp949 (HWP/CSV), UTF-8 (그 외) |
| LLM API | 프로젝트별 `.env` 파일 관리 |
| 경로 루트 | `${PROJECT_ROOT}` (Claude Code 실행 디렉토리) |

## Windows 특화 주의사항

- **HWP OLE**: 반드시 로컬 Windows 환경에서만 실행 (원격/WSL 불가)
- **경로 공백**: OneDrive 등 공백 포함 경로는 항상 따옴표 처리 (절대경로 하드코딩 금지 준수)
- **인코딩**: cp949 파일은 `open(..., encoding='cp949')` 명시
- **경로 구분자**: Python에서는 `/` 또는 `r"..."` raw string 사용
- **subprocess**: `errors="replace"` 필수 (AER-005)

## 주요 참조 경로/설정값

| 항목 | 경로/값 |
|---|---|
| 용어사전 | `docs/LogManagement/용어사전.md` |
| 세션 대시보드 | `docs/LogManagement/1st_Log.md` |
| bkit matchRateThreshold | 85 |
| bkit maxIterations | 3 |
