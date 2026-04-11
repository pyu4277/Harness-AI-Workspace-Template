---
name: pdf
classification: capability
classification-reason: "PDF 처리 라이브러리 호출 + 005 한국 대학 행정 도메인 통합. 모델 독립적, 라이브러리 의존"
deprecation-risk: low
description: |
  PDF 파일에 대한 모든 작업을 자동화합니다. 텍스트/표 추출, 병합/분할/회전,
  워터마크/암호화, 신규 PDF 생성, 폼 작성, 이미지 추출, OCR(스캔 PDF) 등
  Anthropic 공식 PDF skill (github.com/anthropics/skills/skills/pdf)을
  vendor + 한국화한 스킬입니다.

  Use proactively when:
  - 사용자가 .pdf 파일을 언급할 때
  - PDF에서 텍스트/표/이미지 추출 요청 시
  - PDF 병합/분할/회전/워터마크 요청 시
  - 신규 PDF 생성 요청 시 (보고서/송장/명세서 등)
  - PDF 폼 채우기 요청 시
  - 스캔 PDF의 OCR 요청 시
  - 005 도메인: 200_사업/300_제일대학교의 PDF 자료 발췌 시

  Triggers: pdf, PDF, .pdf, PDF 파일, 보고서, 계획서, 양식, 폼,
  텍스트 추출, 표 추출, 병합, 분할, 회전, 워터마크, 암호, OCR, 스캔,
  PDF 작성, PDF 생성, 송장, 명세서, 한글 PDF, 학술 논문 PDF

  Do NOT use for: HWPX 한글 파일 (HWPX_Master 사용),
  DOCX/XLSX/PPTX (DocKit 사용), Markdown (mdGuide 사용)
argument-hint: "[task] [file]"
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
imports:
  - .agents/skills/pdf/scripts/check_fillable_fields.py
  - .agents/skills/pdf/scripts/extract_form_field_info.py
  - .agents/skills/pdf/scripts/extract_form_structure.py
  - .agents/skills/pdf/scripts/convert_pdf_to_images.py
  - .agents/skills/pdf/scripts/check_bounding_boxes.py
  - .agents/skills/pdf/scripts/create_validation_image.py
  - .agents/skills/pdf/scripts/fill_fillable_fields.py
  - .agents/skills/pdf/scripts/fill_pdf_form_with_annotations.py
---

# PDF 처리 가이드 (한국어, 005 통합)

> **vendor 출처**: `github.com/anthropics/skills/skills/pdf` (commit `12ab35c`)
> **영문 원본**: [SKILL.en.md](SKILL.en.md) -- Anthropic 공식 영문 가이드
> **고급 reference**: [reference.md](reference.md) (한국어) / [reference.en.md](reference.en.md) (영문)
> **폼 작성**: [forms.md](forms.md) (한국어) / [forms.en.md](forms.en.md) (영문)
> **라이선스**: [LICENSE.txt](LICENSE.txt) (Anthropic Proprietary)
> **출처 + 사용 범위**: [ATTRIBUTION.md](ATTRIBUTION.md)

## 개요

본 스킬은 Python 라이브러리(`pypdf`, `pdfplumber`, `reportlab` 등)와 CLI 도구(`qpdf`, `pdftotext`, `pdfimages`)를 사용하여 PDF의 모든 처리를 자동화합니다. 005_AI_Project의 한국 대학 행정/연구 자동화 도메인에 통합되어 있습니다.

### 005 도메인 사용 사례

| 작업 | 도구 조합 |
|------|----------|
| **200_사업 PDF 7개 발췌** | wiki-pdf-stage.js (임시 복사) → pdfplumber 텍스트 추출 → wiki entity |
| **연구 논문 PDF 분석** | PaperResearch (검색 + 다운로드) → pdf 스킬 (메타 + 본문 추출) → llm-wiki (entity) |
| **HWPX → PDF 변환 후 처리** | HWPX_Master (HWPX 처리) → external 변환 → pdf 스킬 |
| **출장 신청서/계획서 PDF 자동 작성** | reportlab + pypdf (양식 채우기) |
| **사업 보고서 표 추출 → Excel** | pdfplumber → pandas → openpyxl |
| **스캔 문서 OCR (한국어)** | pdf2image → pytesseract (한국어 모델 `kor`) |

## Quick Start

### 1. 텍스트 추출 (가장 흔한 작업)

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    print(text)
```

### 2. 페이지 수 + 메타데이터

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
print(f"페이지: {len(reader.pages)}")
print(f"제목: {reader.metadata.title}")
print(f"저자: {reader.metadata.author}")
```

### 3. 첫 N 페이지만 추출 (대용량 PDF 발췌)

```python
import pdfplumber

with pdfplumber.open("large.pdf") as pdf:
    for i in range(min(5, len(pdf.pages))):  # 첫 5 페이지
        text = pdf.pages[i].extract_text() or ""
        print(f"=== 페이지 {i+1} ===")
        print(text)
```

## Python 라이브러리 (4종)

### pypdf (BSD) -- 기본 작업

| 작업 | 함수 |
|------|------|
| 읽기 | `PdfReader(path)` |
| 쓰기 | `PdfWriter()` |
| 페이지 추가 | `writer.add_page(page)` |
| 회전 | `page.rotate(90)` |
| 메타데이터 | `reader.metadata.title` |
| 암호화 | `writer.encrypt("user_pw", "owner_pw")` |
| 폼 필드 확인 | `reader.get_fields()` |
| 폼 필드 갱신 | `writer.update_page_form_field_values(...)` |

#### PDF 병합

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for f in ["a.pdf", "b.pdf", "c.pdf"]:
    reader = PdfReader(f)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as out:
    writer.write(out)
```

#### PDF 분할 (페이지별)

```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as out:
        writer.write(out)
```

### pdfplumber (MIT) -- 텍스트 + 표 추출

#### 표 추출 (한국어 표 잘 작동)

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("report.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

if all_tables:
    combined = pd.concat(all_tables, ignore_index=True)
    combined.to_excel("extracted.xlsx", index=False)
```

#### 좌표 기반 영역 추출

```python
with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    bbox = (100, 100, 400, 200)  # left, top, right, bottom
    region_text = page.within_bbox(bbox).extract_text()
```

### reportlab (BSD) -- PDF 신규 생성

#### 기본 PDF 생성

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=A4)
width, height = A4

# 한국어 폰트 등록 필요 (별도 다운로드)
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# pdfmetrics.registerFont(TTFont('NanumGothic', 'NanumGothic.ttf'))
# c.setFont('NanumGothic', 12)

c.drawString(100, height - 100, "Hello PDF!")
c.save()
```

> **한국어 출력 주의**: 기본 폰트는 한국어 글리프 미포함. NanumGothic 또는 시스템 폰트를 등록 필수.

#### 표가 있는 보고서 생성

```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

doc = SimpleDocTemplate("report.pdf")
elements = []

styles = getSampleStyleSheet()
elements.append(Paragraph("Quarterly Report", styles['Title']))

data = [
    ['Item', 'Q1', 'Q2', 'Q3', 'Q4'],
    ['Sales', '100', '120', '135', '150'],
    ['Cost', '80', '90', '100', '110'],
]
table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.grey),
    ('GRID', (0,0), (-1,-1), 1, colors.black),
]))
elements.append(table)

doc.build(elements)
```

> **중요 (IMP-021 유사)**: 유니코드 첨자/위첨자 (₀₁₂₃ ⁰¹²³) 사용 금지. 기본 폰트가 글리프 미포함이라 검은 박스로 렌더링됨. 대신 ReportLab XML 마크업 사용:
> ```python
> Paragraph("H<sub>2</sub>O", styles['Normal'])
> Paragraph("x<super>2</super>", styles['Normal'])
> ```

### pypdfium2 (Apache/BSD) -- 빠른 렌더링

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
for i, page in enumerate(pdf):
    bitmap = page.render(scale=2.0)
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.png")
```

자세한 사용법은 [reference.md](reference.md) 참조.

## CLI 도구 (선택)

### pdftotext (poppler-utils, GPL-2)

```bash
# 텍스트 추출
pdftotext input.pdf output.txt

# 레이아웃 보존
pdftotext -layout input.pdf output.txt

# 페이지 범위
pdftotext -f 1 -l 5 input.pdf output.txt

# bbox 좌표 포함 XML
pdftotext -bbox-layout input.pdf output.xml
```

### qpdf (Apache)

```bash
# 병합
qpdf --empty --pages a.pdf b.pdf -- merged.pdf

# 페이지 범위 추출
qpdf input.pdf --pages . 1-5 -- extracted.pdf

# 회전
qpdf input.pdf output.pdf --rotate=+90:1

# 암호 해제
qpdf --password=secret --decrypt encrypted.pdf decrypted.pdf

# 페이지 그룹 분할
qpdf --split-pages=10 input.pdf out_%02d.pdf

# 손상된 PDF 복구
qpdf --check broken.pdf
qpdf --replace-input broken.pdf
```

### pdfimages (poppler-utils)

```bash
# 모든 이미지 추출 (원본 형식)
pdfimages -all input.pdf img_prefix

# JPEG 형식 + 페이지 번호
pdfimages -j -p input.pdf images/page
```

## 자주 쓰는 작업

### 1. 스캔 PDF의 OCR (한국어)

```python
# pip install pytesseract pdf2image
# tesseract-ocr 한국어 모델: tessdata/kor.traineddata 필요
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf", dpi=300)
text = ""
for i, image in enumerate(images):
    text += f"\n=== 페이지 {i+1} ===\n"
    text += pytesseract.image_to_string(image, lang='kor')
print(text)
```

### 2. 워터마크 추가

```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as out:
    writer.write(out)
```

### 3. 폼 채우기

`forms.md` 한국어 가이드 참조. 스킬 작업 흐름:

1. `python scripts/check_fillable_fields.py <input.pdf>` -- fillable 필드 존재 여부 확인
2. **fillable 있음**:
   - `python scripts/extract_form_field_info.py <input.pdf> <field_info.json>`
   - `field_values.json` 작성 (사용자 입력)
   - `python scripts/fill_fillable_fields.py <input.pdf> <field_values.json> <output.pdf>`
3. **fillable 없음**:
   - `python scripts/extract_form_structure.py <input.pdf> <form_structure.json>`
   - `python scripts/convert_pdf_to_images.py <input.pdf> <images/>`
   - `fields.json` 작성 (좌표 + 채울 텍스트)
   - `python scripts/check_bounding_boxes.py <fields.json>`
   - `python scripts/fill_pdf_form_with_annotations.py <input.pdf> <fields.json> <output.pdf>`
   - `python scripts/create_validation_image.py 1 <fields.json> <input_img> <validation.png>` (검증)

### 4. 위키 폴더 PDF 발췌 (005 통합)

```bash
# 1. wiki-pdf-stage.js로 005 임시 복사 (PDF MCP allowed list 우회)
node .claude/hooks/wiki-pdf-stage.js stage \
  "D:/OneDrive - 순천대학교/001_Wiki_AI/000_Raw/.../document.pdf"
# 출력: D:\...\Temporary Storage\wiki-pdf-stage\document.pdf

# 2. Python으로 발췌
python -c "
import pdfplumber
with pdfplumber.open(r'D:\OneDrive - 순천대학교\005_AI_Project\Temporary Storage\wiki-pdf-stage\document.pdf') as pdf:
    for i in range(min(5, len(pdf.pages))):
        print(f'=== 페이지 {i+1} ===')
        print(pdf.pages[i].extract_text() or '')
"

# 3. 발췌 결과를 wiki entity로 작성

# 4. cleanup
node .claude/hooks/wiki-pdf-stage.js cleanup
```

## Quick Reference

| 작업 | 권장 도구 | 명령/코드 |
|------|----------|----------|
| 텍스트 추출 | pdfplumber | `page.extract_text()` |
| 표 추출 | pdfplumber | `page.extract_tables()` |
| 메타데이터 | pypdf | `reader.metadata.title` |
| 병합 | pypdf | `writer.add_page(page)` |
| 분할 | pypdf 또는 qpdf | 페이지별 또는 `qpdf --split-pages=N` |
| 회전 | pypdf | `page.rotate(90)` |
| 워터마크 | pypdf | `page.merge_page(watermark)` |
| 암호화 | pypdf | `writer.encrypt(...)` |
| OCR (스캔) | pdf2image + pytesseract | `pytesseract.image_to_string(image, lang='kor')` |
| 신규 생성 | reportlab | Canvas 또는 Platypus |
| 빠른 렌더링 | pypdfium2 | `pdf[0].render(scale=2.0)` |
| 폼 채우기 | scripts/* | 위 "폼 채우기" 절차 |
| CLI 텍스트 | pdftotext | `pdftotext -layout in.pdf out.txt` |
| CLI 병합 | qpdf | `qpdf --empty --pages a.pdf b.pdf -- merged.pdf` |
| CLI 이미지 | pdfimages | `pdfimages -all in.pdf prefix` |

## 005_AI_Project 통합 + 다른 스킬과의 관계

| 다른 스킬 | 본 스킬과의 관계 |
|----------|-----------------|
| **HWPX_Master** (Tier-A, 4-Track) | HWPX는 한글 정부 양식 전용. PDF 변환 후 본 스킬 사용 |
| **DocKit** (Tier-B, 3-Track) | DOCX/PPTX 통합 (PDF는 Track 1에 부분). 본 스킬이 PDF 전용 |
| **PaperResearch** (Tier-A, Linear Pipeline) | 학술 논문 검색 + Search & Log. 다운로드 후 본 스킬로 발췌 |
| **mdGuide** (Tier-B, Branching+Linear) | 발췌 결과 .md를 mdGuide로 검증 |
| **VisualCapture** (Tier-A, Conditional Step) | 화면 캡처 PDF는 OCR (pytesseract) 적용 |
| **llm-wiki** (Tier-A, Operation Dispatcher) | 발췌 결과를 wiki entity로 ingest |
| **wiki-pdf-stage.js** (.claude/hooks) | 위키 폴더 PDF를 005 임시 복사 (PDF MCP allowed list 우회) |

## 의존성 설치

### Python (이미 설치됨, 2026-04-11 검증)

005 환경에서는 다음 9 패키지가 이미 설치되어 있습니다:

| 패키지 | 버전 |
|--------|------|
| pypdf | 6.10.0 |
| pdfplumber | 0.11.9 |
| reportlab | 4.4.10 |
| pypdfium2 | 5.7.0 |
| pytesseract | 0.3.13 |
| pdf2image | 1.17.0 |
| Pillow (PIL) | 12.2.0 |
| pandas | 3.0.2 |
| openpyxl | 3.1.5 |

**Python 실행 경로** (PATH 미등록, 직접 호출):
```bash
"C:/Users/pyu42/AppData/Local/Programs/Python/Python312/python.exe" -m <module>
```

재설치 시:
```bash
"C:/Users/pyu42/AppData/Local/Programs/Python/Python312/python.exe" -m pip install \
  pypdf pdfplumber reportlab pypdfium2 pytesseract pdf2image Pillow pandas openpyxl
```

### CLI 도구 (이미 설치됨, 2026-04-11 검증, Windows)

| 도구 | 버전 | 경로 |
|------|------|------|
| qpdf | 12.3.2 | `C:\Program Files\qpdf 12.3.2\bin\qpdf.exe` |
| tesseract | 5.4.0 | `C:\Program Files\Tesseract-OCR\tesseract.exe` |
| pdftotext (poppler) | 25.07.0 | `C:\Users\pyu42\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_*/poppler-25.07.0/Library/bin/pdftotext.exe` |
| tesseract 한국어 모델 | -- | `C:\Users\pyu42\tessdata\kor.traineddata` (사용자 폴더, Program Files 권한 거부 회피) |

**Tesseract 한국어 사용 시**: `--tessdata-dir "C:\Users\pyu42\tessdata"` 명시 (tessdata가 사용자 폴더에 있으므로):
```python
import pytesseract
custom_config = r'--tessdata-dir "C:\Users\pyu42\tessdata"'
text = pytesseract.image_to_string(image, lang='kor', config=custom_config)
```

### 재설치 (Windows winget)

```powershell
winget install --id Python.Python.3.12 --silent
winget install --id qpdf.qpdf --silent
winget install --id UB-Mannheim.TesseractOCR --silent
winget install --id oschwartz10612.Poppler --silent

# 한국어 OCR 모델 (관리자 권한 없으므로 사용자 폴더):
mkdir C:\Users\pyu42\tessdata
# Python으로 다운로드:
python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata', 'C:/Users/pyu42/tessdata/kor.traineddata')"
```

### CLI 도구 (Linux)

```bash
sudo apt install qpdf poppler-utils tesseract-ocr tesseract-ocr-kor
```

### CLI 도구 (macOS)

```bash
brew install qpdf poppler tesseract tesseract-lang
```

## 제약사항

- **이모티콘 금지** (IMP-021): Navigator/문서의 표 마커는 ASCII만 사용. reportlab 출력 PDF에도 유니코드 첨자/위첨자 사용 금지
- **절대경로 금지**: 모든 경로는 005 루트 또는 위키 루트 기준 상대경로 (단, wiki-pdf-stage 호출 시 위키 PDF는 절대경로 필요)
- **한국어 폰트**: reportlab으로 한국어 PDF 생성 시 NanumGothic 등 한국어 폰트 등록 필수
- **OCR 한국어 모델**: pytesseract 사용 시 `kor.traineddata`가 tessdata 폴더에 있어야 함
- **대용량 PDF**: 32 MB 이상 또는 100+ 페이지는 페이지 단위 lazy 처리 권장 (pdfplumber)
- **암호화 PDF**: `reader.is_encrypted` 확인 + `reader.decrypt(password)` 필요
- **손상 PDF**: `qpdf --check`로 진단, `qpdf --replace-input`으로 복구 시도
- **scripts/ 수정 금지**: 8 vendor 스크립트는 영문 그대로 (라이선스 + 동기화 편의)

## 라이선스

- **본 스킬 (vendor 부분)**: Anthropic Proprietary -- `LICENSE.txt` 참조
- **사용 범위**: 005_AI_Project 내부 사용만 (외부 공개 금지). 자세한 내용은 `ATTRIBUTION.md`
- **Python 라이브러리**: 각 라이브러리별 별도 라이선스 (BSD/MIT/Apache 등). `ATTRIBUTION.md` 참조

## 갱신 이력

| 일자 | 변경 | 출처 |
|------|------|------|
| 2026-04-11 | Tier-A 신규 생성 (vendor + 한국화) | `github.com/anthropics/skills/skills/pdf` (commit `12ab35c`) |
