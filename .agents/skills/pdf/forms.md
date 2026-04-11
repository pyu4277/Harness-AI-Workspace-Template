# PDF 폼 작성 가이드 (한국어 wrapper)

> **vendor 영문 원본**: [forms.en.md](forms.en.md) -- 모든 단계 + 상세 코드
> **메인 가이드**: [SKILL.md](SKILL.md)
> **본 문서**: 영문 원본의 한국어 가이드 + 005 통합 노트

---

## **중요: 순서대로 실행. 코드 작성으로 건너뛰기 금지.**

## Step 0: Fillable 필드 존재 여부 확인

```bash
cd .agents/skills/pdf
python scripts/check_fillable_fields.py <file.pdf>
```

결과에 따라 다음 두 경로 중 하나로 진행:
- **fillable 있음** → "A. Fillable 필드 처리" 진행
- **fillable 없음** → "B. Non-fillable 필드 처리" 진행

---

## A. Fillable 필드 처리 (구조화된 폼)

### A.1 필드 정보 추출

```bash
python scripts/extract_form_field_info.py <input.pdf> <field_info.json>
```

**field_info.json 구조** (5 필드 유형):

```json
[
  {
    "field_id": "last_name",
    "page": 1,
    "rect": [left, bottom, right, top],
    "type": "text"
  },
  {
    "field_id": "Checkbox12",
    "page": 1,
    "type": "checkbox",
    "checked_value": "/On",
    "unchecked_value": "/Off"
  },
  {
    "field_id": "Gender",
    "page": 1,
    "type": "radio_group",
    "radio_options": [
      {"value": "/M", "rect": [...]},
      {"value": "/F", "rect": [...]}
    ]
  },
  {
    "field_id": "Country",
    "page": 1,
    "type": "choice",
    "choice_options": [
      {"value": "kr", "text": "Korea"},
      {"value": "us", "text": "USA"}
    ]
  }
]
```

### A.2 PDF를 PNG 이미지로 변환 (각 페이지)

```bash
python scripts/convert_pdf_to_images.py <file.pdf> <output_dir>
```

각 이미지를 분석하여 각 폼 필드의 의도/목적 파악. **bbox PDF 좌표를 이미지 좌표로 변환 필수**.

### A.3 field_values.json 작성

채울 값을 명시:

```json
[
  {
    "field_id": "last_name",
    "description": "사용자 성",
    "page": 1,
    "value": "홍길동"
  },
  {
    "field_id": "Checkbox12",
    "description": "18세 이상 체크박스",
    "page": 1,
    "value": "/On"
  }
]
```

**값 유형 (type별)**:
- text: 문자열
- checkbox: `checked_value` 또는 `unchecked_value`
- radio_group: `radio_options[i].value` 중 하나
- choice: `choice_options[i].value` 중 하나

### A.4 폼 채우기

```bash
python scripts/fill_fillable_fields.py <input.pdf> <field_values.json> <output.pdf>
```

스크립트가 field_id + 값 유효성을 검증. 에러 출력 시 field_values.json 수정.

---

## B. Non-fillable 필드 처리 (텍스트 annotation 추가)

PDF에 fillable 필드가 없으면 텍스트 annotation을 그려 채움. **구조 추출 우선 → 시각 추정 fallback**.

### B.1 구조 추출 시도 (Approach A 우선)

```bash
python scripts/extract_form_structure.py <input.pdf> form_structure.json
```

**form_structure.json 내용**:
- `labels` -- 텍스트 요소 (정확한 PDF 좌표)
- `lines` -- 행 경계 수평선
- `checkboxes` -- 작은 사각형 (체크박스)
- `row_boundaries` -- 수평선 기반 row 위치

**결과 확인**:
- 의미 있는 labels 있음 → **Approach A: 구조 기반 좌표** 사용
- labels 없거나 (cid:X) 패턴만 (스캔 PDF) → **Approach B: 시각 추정** 사용

### Approach A: 구조 기반 좌표 (권장)

**좌표계**: PDF 좌표, y=0이 페이지 **상단**, y가 증가하면 아래로.

#### A.1 구조 분석

form_structure.json에서:
1. **레이블 그룹**: 인접 텍스트 요소 (예: "Last" + "Name")
2. **Row 구조**: 같은 `top` 값의 레이블은 같은 행
3. **필드 컬럼**: 입력 영역은 레이블 끝 + gap부터 시작
4. **체크박스**: form_structure.json의 좌표 직접 사용

#### A.2 누락 요소 점검

구조 추출이 놓치는 경우:
- 원형 체크박스 (사각형만 감지)
- 복잡한 그래픽 / 비표준 컨트롤
- 흐릿하거나 밝은 색 요소

→ 누락 시 **Hybrid Approach** 사용 (아래)

#### A.3 fields.json 작성 (PDF 좌표)

**텍스트 필드 좌표 계산**:
- entry x0 = label x1 + 5 (gap)
- entry x1 = 다음 label x0 또는 row 경계
- entry top = label top과 동일
- entry bottom = 다음 row 경계 또는 label bottom + row_height

**체크박스**: form_structure.json에서 직접 좌표 사용

```json
{
  "pages": [
    {"page_number": 1, "pdf_width": 612, "pdf_height": 792}
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "성 입력 필드",
      "field_label": "Last Name",
      "label_bounding_box": [43, 63, 87, 73],
      "entry_bounding_box": [92, 63, 260, 79],
      "entry_text": {"text": "홍길동", "font_size": 10}
    },
    {
      "page_number": 1,
      "description": "한국 거주 체크박스",
      "field_label": "한국",
      "label_bounding_box": [260, 200, 280, 210],
      "entry_bounding_box": [285, 197, 292, 205],
      "entry_text": {"text": "X"}
    }
  ]
}
```

**핵심**: `pdf_width`/`pdf_height` 사용 + form_structure.json의 좌표 직접 사용.

#### A.4 bbox 검증

```bash
python scripts/check_bounding_boxes.py fields.json
```

검증 항목:
- 교차 bbox (텍스트 겹침)
- 폰트 크기 대비 너무 작은 entry box

에러 출력 시 fields.json 수정 후 재실행.

---

### Approach B: 시각 추정 (fallback)

스캔 PDF (전부 (cid:X) 패턴만 있음)에 사용.

#### B.1 PDF → 이미지

```bash
python scripts/convert_pdf_to_images.py <input.pdf> <images_dir/>
```

#### B.2 초기 필드 식별

각 페이지 이미지를 살펴 폼 섹션 + 대략 위치 파악:
- 폼 필드 레이블 + 위치
- 입력 영역 (선/박스/공백)
- 체크박스 + 위치

각 필드의 대략 픽셀 좌표 메모 (정확하지 않아도 OK).

#### B.3 Zoom 정밀화 (정확도 핵심)

각 필드별로 영역을 잘라 좌표 정밀화. **ImageMagick** 사용:

```bash
magick <page_image> -crop <width>x<height>+<x>+<y> +repage <crop_output.png>
```

여기서:
- `<x>, <y>` = crop 영역 좌상단 (대략 추정값 - padding)
- `<width>, <height>` = crop 크기 (필드 영역 + ~50px padding)

**예시**: (100, 150) 근처 "이름" 필드 정밀화:
```bash
magick images_dir/page_1.png -crop 300x80+50+120 +repage crops/name_field.png
```

(`magick` 없으면 `convert` 시도)

**잘린 이미지 검토**:
1. 입력 영역 시작 픽셀 식별 (레이블 끝 다음)
2. 입력 영역 끝 픽셀 식별 (다음 필드 또는 가장자리)
3. 입력 선/박스의 상단 + 하단 식별

**Crop 좌표를 전체 이미지 좌표로 변환**:
- full_x = crop_x + crop_offset_x
- full_y = crop_y + crop_offset_y

예: crop이 (50, 120)에서 시작하고 entry box가 crop 안에서 (52, 18)에 있으면:
- entry_x0 = 52 + 50 = 102
- entry_top = 18 + 120 = 138

각 필드 반복. 인접 필드는 단일 crop으로 그룹화 가능.

#### B.4 fields.json 작성 (이미지 좌표)

```json
{
  "pages": [
    {"page_number": 1, "image_width": 1700, "image_height": 2200}
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "성 입력 필드",
      "field_label": "Last Name",
      "label_bounding_box": [120, 175, 242, 198],
      "entry_bounding_box": [255, 175, 720, 218],
      "entry_text": {"text": "홍길동", "font_size": 10}
    }
  ]
}
```

**핵심**: `image_width`/`image_height` 사용 + zoom 분석에서 얻은 정밀 픽셀 좌표.

#### B.5 bbox 검증

```bash
python scripts/check_bounding_boxes.py fields.json
```

---

### Hybrid Approach: 구조 + 시각

구조 추출이 대부분 성공하지만 일부 요소(원형 체크박스 등)를 놓칠 때.

1. 감지된 필드 → **Approach A** 사용
2. 누락 필드 → PDF → 이미지 변환 + 시각 분석
3. 누락 필드만 **Approach B**의 zoom 정밀화 사용
4. **좌표 통합**: 모든 좌표를 PDF 좌표로 변환:
   - pdf_x = image_x * (pdf_width / image_width)
   - pdf_y = image_y * (pdf_height / image_height)
5. fields.json은 단일 좌표계 사용 (`pdf_width`/`pdf_height`)

---

## Step 2: 채우기 전 검증

```bash
python scripts/check_bounding_boxes.py fields.json
```

검증:
- 교차 bbox (겹침 방지)
- 폰트 크기 대비 entry box 크기

에러 수정 후 진행.

## Step 3: 폼 채우기

스크립트가 좌표계 (`pdf_width` vs `image_width`)를 자동 감지:

```bash
python scripts/fill_pdf_form_with_annotations.py <input.pdf> fields.json <output.pdf>
```

## Step 4: 출력 검증

채워진 PDF를 이미지로 변환하여 텍스트 위치 검증:

```bash
python scripts/convert_pdf_to_images.py <output.pdf> <verify_images/>
```

텍스트 잘못 위치 시:
- **Approach A**: form_structure.json의 PDF 좌표 + `pdf_width`/`pdf_height` 확인
- **Approach B**: 이미지 dimensions + 정확한 픽셀 좌표 확인
- **Hybrid**: 시각 추정 필드의 좌표 변환 정확성 확인

검증 이미지 자동 생성도 가능:
```bash
python scripts/create_validation_image.py 1 fields.json <input_img.png> <validation.png>
```
- 빨간 박스 = entry bbox
- 파란 박스 = label bbox

---

## 005_AI_Project 사용 사례

### 사례 1: 200_사업의 출장 신청서 자동화

200_사업 폴더의 출장 양식 (md 형식)을 PDF로 변환 후 본 스킬로 자동 채움:

```
사용자 입력 (소속 / 직위 / 출장지 / 출장 목적 등)
→ field_values.json 또는 fields.json
→ fill_fillable_fields.py 또는 fill_pdf_form_with_annotations.py
→ 채워진 PDF
```

### 사례 2: 정부 공문 양식 채우기

HWPX_Master로 hwpx → PDF 변환 후 본 스킬로 fillable 필드 채움.

### 사례 3: 평가 체크리스트 자동 작성

Evaluation_Skill_Genesis entity의 평가 항목 → fields.json → check 후 채우기.

---

## 영문 원본 참조

본 한국어 forms는 영문 [forms.en.md](forms.en.md)의 한국어 가이드입니다. 모든 단계 + 코드 예제는 영문 원본 참조.

## 라이선스

본 스킬 (vendor 부분)은 Anthropic Proprietary. [LICENSE.txt](LICENSE.txt) + [ATTRIBUTION.md](ATTRIBUTION.md) 참조.
