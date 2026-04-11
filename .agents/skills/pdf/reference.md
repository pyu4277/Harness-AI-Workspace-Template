# PDF 처리 고급 Reference (한국어 wrapper)

> **vendor 영문 원본**: [reference.en.md](reference.en.md) -- 모든 코드 예제 + 상세 설명
> **메인 가이드**: [SKILL.md](SKILL.md)
> **본 문서**: 영문 원본의 한국어 요약 + 005 도메인 통합 노트

본 한국어 reference는 영문 원본의 **구조 요약 + 핵심 사용 사례 + 005 통합 가이드**만 다룹니다. 코드 예제 전체는 [reference.en.md](reference.en.md)에서 직접 확인하세요.

---

## 1. pypdfium2 라이브러리 (Apache/BSD)

### 개요

`pypdfium2`는 PDFium (Chromium의 PDF 엔진)의 Python 바인딩. **빠른 PDF 렌더링 + 이미지 변환**에 탁월. PyMuPDF의 무료 대체.

### 핵심 기능

| 작업 | 함수 |
|------|------|
| PDF 로드 | `pdfium.PdfDocument(path)` |
| 페이지 렌더링 | `page.render(scale=2.0, rotation=0)` → bitmap |
| PIL 이미지 변환 | `bitmap.to_pil()` |
| 텍스트 추출 | `page.get_text()` |

### 005 사용 사례

- **CDM PDF 발췌 시**: pdfplumber가 한국어 처리 어려우면 fallback으로 사용
- **시각 자료 추출**: VisualCapture 스킬과 연계 (PDF → 이미지)
- **첫 페이지 미리보기**: scale=1.0으로 빠른 썸네일 생성

### 영문 원본 코드 위치

[reference.en.md](reference.en.md) → "pypdfium2 Library" 섹션

---

## 2. JavaScript 라이브러리 (선택)

### pdf-lib (MIT)

JavaScript 환경에서 PDF 생성/수정. Node.js 또는 브라우저 동작.

**용도**:
- 005에서는 사용 안 함 (Python 우선)
- 단, ServiceMaker 스킬에서 N8N 워크플로우 설계 시 참고 가능

**핵심 기능**:
- `PDFDocument.load(bytes)` -- 기존 PDF 로드
- `pdfDoc.addPage(...)` -- 페이지 추가
- `page.drawText(...)` -- 텍스트 그리기
- `pdfDoc.copyPages(srcDoc, [indices])` -- 페이지 복사 (병합)
- `pdfDoc.save()` -- 바이트 출력

**영문 코드**: [reference.en.md](reference.en.md) → "pdf-lib (MIT License)" 섹션

### pdfjs-dist (Apache)

Mozilla의 PDF.js. **브라우저에서 PDF 렌더링** 전용.

**용도**:
- 005에서는 사용 안 함
- 웹 기반 PDF 뷰어 구축 시 참고

**영문 코드**: [reference.en.md](reference.en.md) → "pdfjs-dist (Apache License)" 섹션

---

## 3. CLI 도구 고급 활용

### poppler-utils 고급

| 작업 | 명령 |
|------|------|
| bbox 좌표 포함 XML | `pdftotext -bbox-layout input.pdf out.xml` |
| 고해상도 PNG | `pdftoppm -png -r 300 input.pdf prefix` |
| 페이지 범위 + 고해상도 | `pdftoppm -png -r 600 -f 1 -l 3 input.pdf high_res` |
| JPEG 품질 지정 | `pdftoppm -jpeg -jpegopt quality=85 -r 200 input.pdf jpeg` |
| 이미지 메타데이터 | `pdfimages -j -p input.pdf page` |
| 이미지 정보만 | `pdfimages -list input.pdf` |
| 모든 형식 추출 | `pdfimages -all input.pdf img/img` |

### qpdf 고급

| 작업 | 명령 |
|------|------|
| 페이지 그룹 분할 | `qpdf --split-pages=3 input.pdf out_%02d.pdf` |
| 복잡한 페이지 범위 | `qpdf input.pdf --pages input.pdf 1,3-5,8,10-end -- ext.pdf` |
| 다중 PDF 부분 병합 | `qpdf --empty --pages a.pdf 1-3 b.pdf 5-7 c.pdf 2,4 -- combined.pdf` |
| 웹 최적화 | `qpdf --linearize input.pdf optimized.pdf` |
| 압축 최적화 | `qpdf --optimize-level=all input.pdf compressed.pdf` |
| PDF 구조 검사 | `qpdf --check input.pdf` |
| 손상 복구 | `qpdf --fix-qdf damaged.pdf repaired.pdf` |
| 구조 표시 | `qpdf --show-all-pages input.pdf > structure.txt` |
| 256-bit 암호화 | `qpdf --encrypt user_pw owner_pw 256 --print=none --modify=none -- in.pdf enc.pdf` |
| 암호화 상태 | `qpdf --show-encryption encrypted.pdf` |
| 암호 해제 | `qpdf --password=secret --decrypt enc.pdf dec.pdf` |

### 005 사용 사례

- **200_사업 PDF 7개 일괄 처리**: `qpdf --split-pages` + 페이지별 pdfplumber
- **손상 PDF 복구**: 첨부된 PDF가 열리지 않으면 `qpdf --check` 진단
- **시각 자료 추출**: `pdfimages -all`로 모든 이미지 추출 후 VisualCapture 연계

---

## 4. pdfplumber 고급

### 정밀 좌표 추출

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    chars = page.chars
    for char in chars[:10]:
        print(f"'{char['text']}' at x:{char['x0']:.1f} y:{char['y0']:.1f}")

    # bbox 영역 추출 (left, top, right, bottom)
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

### 고급 표 추출 (커스텀 설정)

```python
import pdfplumber

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15
    }
    tables = page.extract_tables(table_settings)

    # 시각 디버깅
    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

### 005 사용 사례

- **순천제일대 신산업사업단 보고서 표 추출**: 복잡한 한국어 표는 `vertical_strategy: "lines"` 권장
- **OCR Grok에서 추출한 MKS/CGS 변환표** 검증: pdfplumber로 원본 PDF에서 동일 추출 후 비교

---

## 5. reportlab 고급 (전문 보고서)

### Table + TableStyle

영문 원본 [reference.en.md](reference.en.md)의 "Create Professional Reports with Tables" 섹션 참조.

**핵심 스타일 옵션**:
- `BACKGROUND` -- 배경색
- `TEXTCOLOR` -- 글자색
- `ALIGN` -- 정렬
- `FONTNAME` -- 폰트 (한국어는 NanumGothic 등록 필수)
- `FONTSIZE` -- 크기
- `GRID` -- 격자
- `BOX` -- 외곽선

### 005 사용 사례

- **출장 신청서 자동 생성**: 200_사업의 출장 양식을 reportlab으로 재현
- **CQI 보고서 자동 생성**: 200_사업의 매뉴얼 개발 방법을 따라 표 + 본문 구성

---

## 6. 복잡한 워크플로우

### 그림/이미지 추출 (PDF에서)

#### 방법 1: pdfimages (가장 빠름)

```bash
pdfimages -all document.pdf images/img
```

#### 방법 2: pypdfium2 + 이미지 처리

영문 [reference.en.md](reference.en.md)의 "Method 2: Using pypdfium2 + Image Processing" 참조. numpy로 비백색 영역 감지.

### 배치 PDF 처리

```python
import os, glob, logging
from pypdf import PdfReader, PdfWriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_extract_text(input_dir):
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            output = pdf_file.replace('.pdf', '.txt')
            with open(output, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"OK: {pdf_file}")
        except Exception as e:
            logger.error(f"FAIL {pdf_file}: {e}")
```

### 005 사용 사례

- **200_사업 PDF 7개 일괄 텍스트 추출**: 위 batch_extract_text 사용
- **300_제일대학교 PDF 일괄 메타 추출**: PDF 폴더 스캔 + 메타데이터 CSV

### PDF Cropping

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.mediabox.left = 50
page.mediabox.bottom = 50
page.mediabox.right = 550
page.mediabox.top = 750

writer.add_page(page)
with open("cropped.pdf", "wb") as out:
    writer.write(out)
```

---

## 7. 성능 최적화 팁

### 대용량 PDF (100+ 페이지 또는 32 MB+)

- 메모리 한 번에 로드 금지 → 페이지 단위 lazy 처리
- `qpdf --split-pages=10` 으로 분할 후 개별 처리
- `pypdfium2`가 가장 빠름 (특히 렌더링)

### 텍스트 추출 우선순위

1. `pdftotext -bbox-layout` (가장 빠름)
2. `pdfplumber.page.extract_text()` (구조화 데이터, 표)
3. `pypdf.extract_text()` (대용량 부적합)
4. `pypdfium2.page.get_text()` (백업)

### 이미지 추출

- 빠름: `pdfimages -all` (CLI)
- 정밀: `pypdfium2.render(scale=N)` (Python)

### 폼 채우기

- pdf-lib (JS)이 폼 구조 가장 잘 보존
- 채우기 전 fields.json 검증 필수 (`check_bounding_boxes.py`)

### 메모리 관리

```python
def process_large_pdf(path, chunk_size=10):
    reader = PdfReader(path)
    total = len(reader.pages)
    for start in range(0, total, chunk_size):
        end = min(start + chunk_size, total)
        writer = PdfWriter()
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        with open(f"chunk_{start//chunk_size}.pdf", "wb") as out:
            writer.write(out)
```

---

## 8. 트러블슈팅

### 암호화 PDF

```python
from pypdf import PdfReader

try:
    reader = PdfReader("encrypted.pdf")
    if reader.is_encrypted:
        reader.decrypt("password")
except Exception as e:
    print(f"복호화 실패: {e}")
```

### 손상된 PDF

```bash
qpdf --check corrupted.pdf
qpdf --replace-input corrupted.pdf
```

### 텍스트 추출 실패 (스캔 PDF)

```python
import pytesseract
from pdf2image import convert_from_path

def extract_with_ocr(path):
    images = convert_from_path(path, dpi=300)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image, lang='kor')  # 한국어
    return text
```

### 한국어 PDF 인코딩 깨짐

순서대로 시도:
1. `pdfplumber` (UTF-8)
2. `pypdfium2.get_text()`
3. `pdftotext -layout` (CLI, UTF-8)
4. OCR fallback (pytesseract + lang='kor')

### reportlab 한국어 출력 검은 박스

NanumGothic 등 한국어 TTF 폰트 등록 필수:
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('NanumGothic', 'C:/Windows/Fonts/malgun.ttf'))
c.setFont('NanumGothic', 12)
```

---

## 9. 라이선스 정보 (라이브러리별)

| 라이브러리 | 라이선스 |
|-----------|---------|
| pypdf | BSD |
| pdfplumber | MIT |
| pypdfium2 | Apache/BSD |
| reportlab | BSD |
| poppler-utils | GPL-2 |
| qpdf | Apache |
| pdf-lib (JS) | MIT |
| pdfjs-dist (JS) | Apache |
| pytesseract | Apache |
| Pillow (PIL) | HPND |

본 스킬 자체 (vendor 부분)는 Anthropic Proprietary. 자세한 내용은 [LICENSE.txt](LICENSE.txt) + [ATTRIBUTION.md](ATTRIBUTION.md) 참조.

---

## 영문 원본 참조

본 한국어 reference는 요약입니다. 모든 코드 예제 + 상세 설명은 [reference.en.md](reference.en.md)에서 확인하세요. 특히:

- pypdfium2 전체 코드 (PDF 렌더링 + 텍스트 추출)
- pdf-lib JavaScript 전체 (PDF 생성/수정/병합)
- pdfjs-dist JavaScript 전체 (브라우저 렌더링)
- pdfplumber 정밀 좌표 + 표 디버깅
- reportlab Table + TableStyle 완전 예제
- 그림 추출 numpy 방법
- 배치 처리 logging 코드
- Cropping 정확한 좌표 계산
- 메모리 청크 처리 코드
