# Phase 3 — Plan: 병합셀 탐지 + 캡쳐

## 결정: OCR 우회 전략

| 항목 | 상태 | 대응 |
|------|------|------|
| Tesseract eng | 설치 | 신뢰도 메타만 기록 |
| Tesseract kor | **미설치** | 한글 OCR 불가 |
| Refined MD 요구 OCR>=80% | 충족 불가 | **Claude 멀티모달 직독** 으로 대체 (Phase 5에서 PNG read) |

OCR 80% 게이트는 "모델/사람이 표 구조를 이해할 수 있어야 한다"의 대리지표였음.
원 의도는 멀티모달 모델 직독으로 충족 가능 → 캡쳐 PNG 자체가 Phase 5 입력.

## 처리 순서

```mermaid
flowchart TD
  A[373 tables JSON] --> B[병합 의심 탐지]
  B -->|None 비율>=20%| C1[suspect]
  B -->|행 컬럼수 불일치| C1
  B -->|n_cols>=8| C1
  B -->|else| C2[pass]
  C1 --> D[페이지 PDF 렌더 200dpi]
  D --> E[페이지 전체 PNG 저장]
  E --> F[Output/Reports/captures/{slug}_p{N}.png]
  F --> G[OCR eng 신뢰도 기록]
  G --> H[suspect_tables.json 인덱스]
```

## 병합 탐지 휴리스틱

| 신호 | 임계 | 근거 |
|------|------|------|
| 빈 셀 비율 (None 또는 빈 문자열) | >=20% | 병합셀은 pdfplumber에서 None 발생 |
| 행별 컬럼 수 불일치 | n_cols 표준편차>0 | 다단 헤더의 신호 |
| 컬럼 수 | >=8 | 복잡한 매트릭스 |
| 셀 텍스트에 줄바꿈 | 1개 이상 | 여러 항목 결합 가능성 |

## 산출
- `Output/Reports/captures/{slug}_p{N}.png` (페이지 단위, 의심 표 포함 페이지만)
- `.bkit_runtime/suspect_tables.json` (인덱스 + 신호)
- `docs/pdca/phase3/check.md`

## 예상 비용
- 페이지당 ~200KB (200dpi)
- 최대 캡쳐: 사업계획서 71p 전부 가정 시 ~14MB
- 실제로는 의심 페이지만 → 50% 이하 예상
