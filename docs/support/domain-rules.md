# 도메인 규칙 -- 한국 대학 연구/행정 특화

> 순천대학교 연구/행정 업무에 특화된 규칙.

---

## HWP 문서 작업

`HWPX_Master` 스킬 최우선 트리거:

| Track | 용도 | 방식 |
|:---|:---|:---|
| Track A | 새 HWPX 생성 | XML 기반 |
| Track B | 기존 HWPX 수정 | XML 직접 조작 |
| Track C | 내용 추출 | 텍스트/표/이미지 |
| Track D | OLE 자동화 | 한글 앱 직접 제어 (Windows 전용) |

## 학술 연구

- `PaperResearch` 스킬로 RISS 자동 검색
- 용어 발견 시 `term-organizer`로 즉시 용어사전 업데이트
- 인용 형식: APA 7th (한국어 논문은 KCI 스타일)

## 보안 규칙

- API 키: 반드시 `.env` 파일 (`.gitignore` 포함)
- HWP OLE: Windows 로컬 실행만 허용
- OneDrive 경로: 공백 포함 경로는 항상 따옴표 처리

## 산출물 형식 가이드

| 용도 | 권장 형식 | 스킬 |
|:---|:---|:---|
| 정부/행정 공문 | .hwpx | HWPX_Master |
| 연구 보고서 | .docx 또는 .pdf | DocKit |
| 발표자료 | .pptx | DocKit |
| 내부 메모/기획 | .md | mdGuide |
| 데이터 분석 결과 | .csv/.xlsx + .md 요약 | -- |
