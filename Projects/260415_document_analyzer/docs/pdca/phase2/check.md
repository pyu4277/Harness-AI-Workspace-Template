# Phase 2 — Check: PDF 파싱 결과 검증

## 파싱 통계 (5/5 성공)

| slug | role | pages | empty | tables | AER-003 |
|------|------|-------|-------|--------|---------|
| plan | Source-Plan | 71 | 1 (1.4%) | 238 | YES (>50p) |
| evidence | Source-Evidence | 50 | 0 | 54 | NO (=50p) |
| pres | Source-Presentation | 2 | 0 | 12 | NO |
| indicator | Reference-Indicator | 1 | 0 | 1 | NO |
| format | Reference-Format | 42 | 0 | 68 | NO |
| **합계** | — | **166** | **1** | **373** | 1건 |

## 게이트
- 5/5 PDF 파싱 OK
- 빈 페이지 비율 1/166 = 0.6% < 30% PASS
- 사업계획서 표 ≥1: 238 PASS
- AER-003 사업계획서 71p에 적용됨 → `.bkit_runtime/text/plan.txt` 생성

## 발견 사항 (Phase 5 분석 입력)

1. **발표자료 2페이지 + 12 표** = 다단 슬라이드 레이아웃. Q3 분석 시 "물리적 페이지" 아닌 "슬라이드 패널" 단위 분해 필요.
2. **사업계획서 71p × 238표** = 페이지당 평균 3.4표 → 표 중심 문서. Q1 cross-doc parity 시 표 셀 단위 비교 필수.
3. **증빙자료 50p 전 페이지 표** = 정량 데이터 집약. Q1 사업계획서 ↔ 증빙자료 비교 시 수치 검증 핵심.
4. **평가지표 1p 1표** = 단일 매트릭스. Q4 채점 기준 추출 단순.
5. **작성서식 42p × 68표** = 단원별 작성 가이드 표. Q2 형식 준수 검증의 골격.

## Phase 3 진입 조건
- 병합셀 후보: 셀 None 비율 높은 표 또는 셀 텍스트가 다음 행으로 이어지는 표 → 다음 단계에서 탐지
- VisualCapture는 병합 의심 표만 선택적 적용 (전수 캡쳐는 비용 과다)
