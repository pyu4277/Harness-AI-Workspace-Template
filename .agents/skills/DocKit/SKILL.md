---
name: DocKit
description: "PDF/DOCX(Word)/PPTX(PowerPoint) 문서 종합 처리 스킬. 텍스트·표 추출, 병합·분할, 생성, 편집, 변경추적 수락, 주석 처리, 슬라이드 제어, OCR 등 비HWP 문서 전 작업에 사용합니다. '.pdf', '.docx', '.pptx', 'PDF', 'Word', '워드', 'PowerPoint', '파워포인트', '발표자료', '보고서 작성' 언급 시 트리거됩니다."
---

# DocKit — 비HWP 문서 종합 처리 스킬

PDF, DOCX(Word), PPTX(PowerPoint) 3가지 포맷을 단일 진입점으로 처리합니다.
HWP/HWPX 파일은 `HWPX_Master` 스킬을 사용하세요.

---

## 포맷별 스크립트 경로

```
DocKit/
├── pdf/scripts/          ← PDF 전용 스크립트
├── docx/scripts/         ← DOCX 전용 스크립트 (office/ 인프라 포함)
└── pptx/scripts/         ← PPTX 전용 스크립트 (office/ 인프라 포함)
```

---

## PDF 기능 (`pdf/scripts/`)

| 스크립트 | 기능 |
|:---|:---|
| `fill_fillable_fields.py` | PDF 폼 필드 채우기 |
| `fill_pdf_form_with_annotations.py` | 주석 기반 폼 채우기 |
| `extract_form_structure.py` | 폼 구조 추출 |
| `extract_form_field_info.py` | 필드 정보 추출 |
| `check_fillable_fields.py` | 채울 수 있는 필드 확인 |
| `check_bounding_boxes.py` | 바운딩 박스 검사 |
| `convert_pdf_to_images.py` | PDF → 이미지 변환 |
| `create_validation_image.py` | 검증 이미지 생성 |

참고 문서: `pdf/reference.md`, `pdf/forms.md`

---

## DOCX 기능 (`docx/scripts/`)

| 스크립트 | 기능 |
|:---|:---|
| `accept_changes.py` | 변경 추적 수락 (redlines 처리) |
| `comment.py` | 주석 추가/조회/삭제 |
| `office/pack.py` | DOCX 압축/해제 |

내부 `office/` 인프라: ISO-IEC29500 스키마, helpers(merge_runs, simplify_redlines)

---

## PPTX 기능 (`pptx/scripts/`)

| 스크립트 | 기능 |
|:---|:---|
| `add_slide.py` | 슬라이드 추가 |
| `clean.py` | 슬라이드 정리 |
| `office/pack.py` | PPTX 압축/해제 |

참고 문서: `pptx/editing.md`, `pptx/pptxgenjs.md`

---

## 실행 방법

```bash
# PDF 예시
python ".agents/skills/DocKit/pdf/scripts/fill_fillable_fields.py" [인자]

# DOCX 예시
python ".agents/skills/DocKit/docx/scripts/accept_changes.py" [인자]

# PPTX 예시
python ".agents/skills/DocKit/pptx/scripts/add_slide.py" [인자]
```

---

## 트리거 판별 기준

| 입력 파일/요청 | 사용 스크립트 |
|:---|:---|
| `.pdf` / PDF 처리 | `pdf/scripts/` |
| `.docx` / Word / 변경추적 | `docx/scripts/` |
| `.pptx` / PowerPoint / 슬라이드 | `pptx/scripts/` |
| HWP / 한글 문서 | HWPX_Master 스킬 사용 |
