---
name: VisualCapture
description: "화면 캡처, 이미지 주석(박스·화살표·하이라이트), Claude Vision 분석 통합 스킬. 에러 화면을 캡처하거나 특정 상황을 이미지로 설명할 때 사용합니다. '스크린샷', '화면 캡처', '에러 캡처', '이미지로 설명', '화면 찍어줘', 'VisualCapture' 키워드 시 트리거됩니다."
---

# VisualCapture — 화면 캡처 + 주석 + 분석 통합 스킬

에러 발생 화면을 캡처하거나, 이미지에 시각적 마커를 추가하거나, Claude Vision으로 분석 보고서를 생성하는 3단계 파이프라인.

스크립트 경로: `.agents/skills/VisualCapture/scripts/`

---

## 3단계 파이프라인

### Step 1: 캡처 (capture.py)

```bash
# 전체 화면
python ".agents/skills/VisualCapture/scripts/capture.py" \
  --out "Projects/YYMMDD_이름/Input/captures/" --name "에러설명"

# 특정 영역 (left top width height)
python ".agents/skills/VisualCapture/scripts/capture.py" \
  --region 0 0 1280 720 --out "Projects/YYMMDD_이름/Input/captures/"

# 특정 창 이름
python ".agents/skills/VisualCapture/scripts/capture.py" \
  --window "한글" --out "Projects/YYMMDD_이름/Input/captures/"
```

### Step 2: 주석 (annotate.py)

| 옵션 | 색상 | 용도 |
|:---|:---:|:---|
| `--box x1,y1,x2,y2` | 빨강 | 오류 영역 강조 |
| `--highlight x1,y1,x2,y2` | 노랑 반투명 | 중요 영역 하이라이트 |
| `--arrow x1,y1,x2,y2` | 파랑 | 흐름·방향 표시 |
| `--text x,y` | 흰색 | 설명 텍스트 삽입 |
| `--label "설명"` | - | 위 요소에 텍스트 추가 |

```bash
python ".agents/skills/VisualCapture/scripts/annotate.py" \
  --input "Input/captures/capture_260401_143022_에러설명.png" \
  --box 100,200,400,350 --label "여기서 오류 발생" \
  --arrow 450,275,405,275 \
  --out "Input/captures/capture_260401_143022_에러설명_annotated.png"
```

### Step 3: 분석 + 보고서 (analyze.py)

```bash
python ".agents/skills/VisualCapture/scripts/analyze.py" \
  --input "Input/captures/capture_annotated.png" \
  --prompt "이 화면의 오류 원인을 분석하고 해결 방법을 알려줘." \
  --out "Output/draft/에러분석보고서.md"
```

---

## 단계 생략 규칙

| 상황 | 실행 단계 |
|:---|:---|
| 화면 캡처만 필요 | Step 1만 |
| 기존 이미지에 마킹만 필요 | Step 2만 |
| 이미지를 AI에게 설명시키기만 필요 | Step 3만 |
| 캡처 → 마킹 → 분석 전체 | Step 1 → 2 → 3 |

---

## 저장 경로 규칙

```
Projects/YYMMDD_이름/
└── Input/
    └── captures/        ← 원본 캡처 + 주석 이미지
Output/
└── draft/               ← analyze.py 보고서 (.md)
```

---

## 의존성

```
pip install pyautogui Pillow pygetwindow anthropic
```

- `pygetwindow`: `--window` 옵션 사용 시만 필요 (Windows 전용)
- `anthropic`: Step 3 분석 시만 필요, API 키는 프로젝트 `.env`에 저장
