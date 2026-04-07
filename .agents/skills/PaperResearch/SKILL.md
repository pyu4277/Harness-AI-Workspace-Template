---
name: PaperResearch
description: "학술 논문 및 연구 자료 자동 검색 스킬. RISS(한국), Google Scholar 등 다국가 DB에서 자동으로 검색어를 생성하고 결과를 엑셀로 정리합니다. '논문', '학술', 'RISS', '학술 검색', 'PaperResearch' 키워드 시 트리거됩니다."
---

# PaperResearch Agent

## 목적

학술 DB 자동 크롤링 → 데이터 정제 → 엑셀 저장까지 자동화하는 학술 연구 지원 스킬.

## 사용법

```
/PaperResearch [연구 주제]
```

예시:
- `/PaperResearch AI 교육`
- `/PaperResearch 중력식 에너지 저장 시스템`

## 실행 절차

스크립트는 현재 활성 프로젝트의 `src/` 아래에 위치합니다.
프로젝트가 없다면 `Projects/_TEMPLATE/`을 복사하여 먼저 생성하세요.

```bash
# 현재 활성 프로젝트 기준 (PROJECT_ROOT 상대경로)
python "Projects/YYMMDD_ProjectName/src/agents/paper_research_agent_curriculum.py" "[주제]"
```

## 검색 대상

- **학술**: RISS (게재논문, 학위논문)
- **특허**: Google 검색 (키워드 "특허" 포함 시)
- **보고서**: Google 검색 (키워드 "보고서" 포함 시)
- **뉴스/홍보**: Google 검색 (키워드 "뉴스", "홍보" 포함 시)

## 출력 구조

`Curriculum_QM_Curated.xlsx` 기준 엑셀 파일:
- 시트: `게재논문`, `학위논문`, `특허`, `보고서`, `홍보자료`, `통합_데이터`
- 데이터 시작: Row 2 (Ghost Row 방지)
- 헤더 자동 주입 (Row 1 누락 시)

## Zero-Defect 데이터 정책

- **Double Write**: 개별 시트 + `통합_데이터` 시트에 동시 저장 (Excel 구버전 호환)
- **자동 복구**: 템플릿 파일 누락 시 63컬럼 스키마로 자동 생성
- **인코딩**: UTF-8 기본, cp949 파일 자동 변환

## 검증

```bash
python tests/verify_integrity_dummy.py
```
