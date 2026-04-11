# Attribution -- PDF Skill 출처 + 라이선스

## 출처

본 PDF 스킬은 **Anthropic 공식 Claude Skills 저장소**에서 vendor 방식으로 가져온 것입니다.

| 항목 | 값 |
|------|------|
| **저장소** | `github.com/anthropics/skills` |
| **경로** | `skills/pdf/` |
| **commit hash** | `12ab35c2eb5668c95810e6a6066f40f4218adc39` |
| **다운로드 일자** | 2026-04-11 |
| **다운로드 방법** | `gh api repos/anthropics/skills/contents/skills/pdf/...` |
| **Raw URL** | `https://raw.githubusercontent.com/anthropics/skills/main/skills/pdf/<file>` |
| **저장소 라이선스** | Proprietary (각 스킬 폴더 LICENSE.txt) |

## 라이선스 (Proprietary)

전문은 `LICENSE.txt` 파일을 참조하세요. © 2025 Anthropic, PBC. All rights reserved.

원본 LICENSE.txt에 명시된 제약사항:
- Services 외부 사본 보관 금지
- 복제/복사 금지 (자동 임시 사본 제외)
- derivative works 금지
- third party 배포 금지
- reverse engineering 금지

## 사용자 결정 + 사용 범위

본 스킬을 005_AI_Project로 가져오는 행위에 대한 **사용자 명시 결정** (2026-04-11):

> "우리가 지금 대화하고 있는 이 프로그램 자체가 Anthropic 프로그램이고 마음껏 사용하라고 공식적으로 공개한거라 모두 그대로 사용해도 아무 문제없어."

→ 사용자 해석:
- 본 대화는 Anthropic의 Claude Code 환경 안에서 진행
- `github.com/anthropics/skills`는 Anthropic이 공식 공개한 자료
- "마음껏 사용하라"는 공개 의도로 해석
- 005_AI_Project 내부 사용은 Services 내 사용으로 간주

### 사용 범위 (사용자 결정 기반)

| 행위 | 허용 |
|------|:---:|
| 005_AI_Project 내부 사용 | OK |
| 한국어 wrapper 작성 (SKILL.md, reference.md, forms.md 한국화) | OK |
| 005 도메인 통합 가이드 추가 | OK |
| Tier-A Navigator 작성 (Track 4-Track) | OK |
| OneDrive 동기화 (개인 백업) | OK |
| 외부 공개 (GitHub public repo, 블로그, 배포) | **금지** -- 별도 사용자 승인 필요 |

## Vendor 파일 목록 (13)

| # | 파일 | 크기 (원본) | 종류 |
|:-:|------|----:|------|
| 1 | `SKILL.en.md` | 8 KB | 메인 가이드 (영문 원본) |
| 2 | `reference.en.md` | 16.7 KB | 고급 reference (pypdfium2 + pdf-lib JS, 영문 원본) |
| 3 | `forms.en.md` | 11.8 KB | PDF 폼 작성 가이드 (영문 원본) |
| 4 | `LICENSE.txt` | 1.5 KB | Proprietary 라이선스 (수정 금지) |
| 5 | `scripts/check_fillable_fields.py` | 0.3 KB | 폼 필드 존재 여부 확인 |
| 6 | `scripts/extract_form_field_info.py` | 4.6 KB | 폼 필드 메타데이터 추출 |
| 7 | `scripts/extract_form_structure.py` | 3.5 KB | 비폼 PDF의 구조 추출 (label/line/checkbox) |
| 8 | `scripts/convert_pdf_to_images.py` | 1.0 KB | PDF → PNG 변환 (페이지별) |
| 9 | `scripts/check_bounding_boxes.py` | 2.8 KB | 폼 채우기 전 bbox 검증 |
| 10 | `scripts/create_validation_image.py` | 1.4 KB | 검증 이미지 생성 (label = blue, entry = red) |
| 11 | `scripts/fill_fillable_fields.py` | 4.2 KB | fillable 필드 채우기 |
| 12 | `scripts/fill_pdf_form_with_annotations.py` | 3.8 KB | 비fillable 폼 텍스트 annotation 추가 |

**합계 13 파일** (4 root + 8 scripts + LICENSE).

## 005_AI_Project 추가 산출물 (vendor 외)

본 스킬에는 vendor 외에 005가 추가한 한국화 + Navigator + 본 ATTRIBUTION 파일이 포함됩니다:

| 파일 | 출처 | 라이선스 |
|------|------|---------|
| `SKILL.md` | 005 작성 (한국어, 005 도메인 통합) | 005_AI_Project 내부 사용 |
| `reference.md` | 005 작성 (한국어 wrapper) | 동일 |
| `forms.md` | 005 작성 (한국어 wrapper) | 동일 |
| `pdf_Navigator.md` | 005 작성 (Tier-A, Track 4-Track) | 동일 |
| `ATTRIBUTION.md` | 005 작성 (본 파일) | 동일 |

## Python 의존성

본 스킬은 **여러 오픈소스 Python 라이브러리에 의존**합니다. 각 라이브러리는 자체 라이선스를 따르며 Anthropic 라이선스와 별개:

| 라이브러리 | 라이선스 | 용도 |
|-----------|---------|------|
| `pypdf` | BSD | 기본 작업 (병합/분할/회전/암호) |
| `pdfplumber` | MIT | 텍스트 + 표 추출 + 구조 분석 |
| `reportlab` | BSD | 신규 PDF 생성 |
| `pypdfium2` | Apache/BSD | 빠른 렌더링 + 이미지 변환 |
| `pytesseract` | Apache | OCR (스캔 PDF) |
| `pdf2image` | MIT | PDF → 이미지 |
| `Pillow (PIL)` | HPND | 이미지 처리 |
| `pdf-lib` (JS) | MIT | JavaScript 환경 (선택) |

CLI 도구:
- `qpdf` (Apache)
- `poppler-utils` (`pdftotext`, `pdfimages`, `pdftoppm`, GPL-2)
- `pdftk` (GPL, 선택)
- `tesseract-ocr` (Apache, OCR 엔진)
- `ImageMagick` (Apache)

## 변경 이력

| 일자 | 변경 | 출처 |
|------|------|------|
| 2026-04-11 | 초기 vendor 다운로드 (commit `12ab35c`) + 한국어 wrapper + Navigator 작성 | github.com/anthropics/skills/skills/pdf |

## 향후 동기화

Anthropic 저장소가 업데이트되면 다음 절차로 동기화:

```bash
# 1. 새 commit hash 확인
gh api repos/anthropics/skills/commits/main --jq '.sha'

# 2. 13 파일 다시 다운로드 + 비교 (diff)
# 3. 변경된 파일만 005에 갱신
# 4. 본 ATTRIBUTION의 commit hash + 변경 이력 갱신
# 5. 한국어 wrapper에도 변경 반영 (수동)
```

## 관련 문서

- `LICENSE.txt` -- Anthropic Proprietary 라이선스 전문
- `SKILL.md` -- 한국어 메인 가이드 (005 통합)
- `SKILL.en.md` -- 영문 원본 메인 가이드 (vendor)
- `reference.md` / `reference.en.md` -- 고급 reference (한국어 + 영문)
- `forms.md` / `forms.en.md` -- 폼 가이드 (한국어 + 영문)
- `pdf_Navigator.md` -- Tier-A Navigator (Track 4-Track)
- `scripts/*.py` -- 8 vendor scripts (수정 금지, 영문 그대로)
