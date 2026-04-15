# Phase 2 — Plan: PDF 파싱 라우팅

## 목표
5개 PDF → 페이지별 텍스트 + 표 JSON. 50p 초과 시 AER-003.

## 도구
- pdfplumber 0.11.9 (텍스트 + 표)
- pypdf 6.10.0 (페이지 수)
- pdfminer.six (대용량 텍스트)
- pdf2image (Phase 3 캡쳐 예약)

## 처리 순서

```mermaid
flowchart TD
  A[5 PDF 입력] --> B[pypdf: 페이지 수 측정]
  B --> C{>50p?}
  C -- YES --> D[AER-003: pdfminer .txt 사전 추출]
  C -- NO --> E[직접 파싱]
  D --> F[pdfplumber: 페이지별 텍스트+표]
  E --> F
  F --> G[.bkit_runtime/pages/{slug}_p{N}.json]
  F --> H[.bkit_runtime/tables/{slug}_p{N}_t{M}.json]
  G --> CHK[검증: 페이지 수 일치 / 빈 페이지 비율 <30%]
```

## 입력 5종 + slug

| slug | 파일 | 역할 |
|------|------|------|
| plan | 사업계획서 | Source-Plan |
| evidence | 증빙자료 | Source-Evidence |
| pres | 발표자료 | Source-Presentation |
| indicator | 평가지표 | Reference-Indicator |
| format | 작성서식 | Reference-Format |

## 검증 게이트
- 5개 PDF 전부 페이지 수 추출 OK
- 빈 페이지(텍스트 길이 0) 비율 <30%
- 표 JSON ≥0 (없어도 OK, 단 사업계획서에는 ≥1 기대)

## 산출
- `.bkit_runtime/pages/{slug}_p{N}.json` (텍스트)
- `.bkit_runtime/tables/{slug}_p{N}_t{M}.json` (표)
- `docs/pdca/phase2/check.md` (요약 통계)
