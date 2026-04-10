# Wiki v3 전면 업그레이드 기획보고서

> Plan Plus 브레인스토밍 + Deep Research 기반. 2026-04-10.

---

## Executive Summary

| 관점 | 내용 |
|---|---|
| **Problem** | 위키에 다양한 유형의 자료(정식 문서, 공문, 업무물, 웹 스크랩, 영상)가 들어오는데, 분류 체계가 정식 발행 문서(KDC)에만 맞춰져 있어 나머지 유형이 체계 없이 방치됨. 동일 자료가 여러 분류에 걸칠 때 "어디에 저장했더라?" 문제 발생 |
| **Solution** | 3축 하이브리드 분류(주제 + 신뢰도 + 프로젝트/맥락) + 바로가기 문서(Cross-Reference Shortcut) 시스템 |
| **Function/UX Effect** | 어떤 분류 경로로 이동하든 관련 자료를 바로가기로 즉시 확인 가능. "이 자료 어디 뒀지?" 고민 제거 |
| **Core Value** | 지식이 분류 체계의 한계에 갇히지 않고, 사용자의 사고 흐름에 맞춰 어디서든 접근 가능 |

---

## 1. User Intent Discovery

### 1-1. 핵심 문제

사용자가 위키에 저장할 자료의 유형이 5가지 이상으로 다양한데, 현재 체계(KDC + 010_Verified)는 정식 발행 문서에만 최적화되어 있음.

### 1-2. 자료 유형 전체 목록

| # | 유형 | 예시 | 신뢰도 |
|---|---|---|---|
| 1 | 정식 발행 문서 | 책, 논문, 특허, 학습교재 | 최고 (동료심사/출판사 검증) |
| 2 | 공적 기관 자료 | 과기부, 행안부, 교육부, 지자체, 관광지 공식 사이트 | 높음 (공적 검증) |
| 3 | 업무 산출물 | 계획서, 보고서, 회의록 | 중간 (내부 검증) |
| 4 | 공문/메일 | 공식 수발신 문서, 업무 메일 | 중간 (발신자 검증) |
| 5 | 개인 프로젝트 | 캡스톤디자인, 과제, 실험 결과 | 중간 (자체 생산) |
| 6 | 공식 웹 콘텐츠 | 정부 포털, 공공 데이터, 법령 정보 | 높음 (기관 운영) |
| 7 | 비정형 웹 스크랩 | 블로그, 나무위키, 커뮤니티 글 | 낮음 (미검증) |
| 8 | 영상/미디어 | YouTube, 강의 영상, 팟캐스트 | 낮음~중간 (채널에 따라) |

### 1-3. 특별 요구사항: 교차 분류 바로가기

**사용자 원문**: "같은 자료가 다른 체계에도 중복되는 분류라면 가장 핵심적인 분류에 본문을 두고 나머지 중복되는 분류에도 바로가기로 등록하여 내 머리에서 떠오르는 체계(분류) 어디로 이동하더라도 해당 자료를 볼 수 있도록"

**캡스톤 논문 예시**: 논문 본문은 `010_Verified/sources/`에 저장. `050_Projects/sources/`에는 바로가기 문서가 생성되어 "캡스톤디자인 -> 논문" 경로로도 접근 가능.

---

## 2. Deep Research 기반 설계

### 2-1. 전문가 체계 비교 분석

| 체계 | 강점 | 약점 | 적용 부분 |
|---|---|---|---|
| **KDC** (한국십진분류법) | 검증된 주제 분류, 국가 표준 | 1문서=1위치 제약 | 주제 분류 골격 (이미 적용) |
| **Faceted Classification** (Ranganathan) | 다차원 동시 분류 | 번호 체계 복잡 | 태그 시스템의 원리로 적용 |
| **MOC** (Nick Milo / LYT) | 교차 분류 해결, 물리적 이동 없이 다중 포함 | MOC 유지 비용 | **바로가기 문서 시스템의 원형** |
| **PARA** (Tiago Forte) | 실행 가능성 기준, 빠른 정리 | 지식 연결 부재 | 프로젝트/아카이브 계층 |
| **Admiralty Code** (NATO) | 출처 신뢰도 2축 독립 평가 | 개인용으로는 과도 | 신뢰도 등급 간소화 적용 |

### 2-2. 3축 하이브리드 분류 설계

Deep Research 결과, 3개 독립 축을 **메타데이터 + 폴더 구조**로 결합하는 것이 최적:

**축 1: 주제 (What)** -- KDC 기반, 이미 구현됨
```
001_General, 100_Philosophy, ..., 500_Technology, ..., 900_History
```

**축 2: 신뢰도/출처 (How Reliable)** -- Admiralty Code 간소화
```
010_Verified     -- 동료심사/출판사 검증 (책, 논문, 특허, 교재)
020_Official     -- 공적 기관 운영 (과기부, 행안부, 교육부, 지자체, 법령)
030_Work         -- 업무 산출물 (계획서, 보고서, 회의록)
040_Correspond   -- 공문/메일 (공식 수발신)
050_Projects     -- 개인 프로젝트 (캡스톤, 과제, 실험)
060_Media        -- 영상/미디어 (YouTube, 강의, 팟캐스트)
070_WebClip      -- 비정형 웹 스크랩 (블로그, 나무위키, 커뮤니티)
```

**축 3: 맥락 (Why/When)** -- 프론트매터 태그로 관리
```yaml
context:
  project: "260401_캡스톤디자인"
  area: "에너지신산업실"
  status: active | archived
```

---

## 3. 바로가기 문서 시스템 (Cross-Reference Shortcut)

### 3-1. 핵심 원리

아키비스트 전통의 "Cross-Reference Card" + Obsidian MOC 패턴을 결합:

- **정본(Canonical)**: 파일 본문은 **가장 핵심적인 분류에 1개만** 존재
- **바로가기(Shortcut)**: 관련된 다른 분류에 **경량 링크 문서** 생성
- **바로가기 문서는 정본이 아님**: 제목 + 한줄 설명 + 정본 링크만 포함

### 3-2. 바로가기 문서 형식

```markdown
---
title: "캡스톤디자인 논문 (바로가기)"
type: shortcut
canonical: "010_Verified/sources/260401_Capstone_PV_Prediction_V001.md"
created: 2026-04-10
---

> 이 문서는 바로가기입니다. 본문은 아래 링크에 있습니다.

[본문 보기: 태양광 발전량 예측 AI 모델 캡스톤 논문](../../010_Verified/sources/260401_Capstone_PV_Prediction_V001.md)

**원본 위치**: 010_Verified/sources/ (정식 발행 논문)
**관련 프로젝트**: 050_Projects/ (캡스톤디자인)
```

### 3-3. 캡스톤 논문 예시 적용

```
논문 본문 (정본):
  010_Verified/sources/260401_Capstone_PV_Prediction_V001.md

바로가기 문서들:
  050_Projects/sources/260401_Capstone_PV_Prediction_V001_SHORTCUT.md
  500_Technology/sources/260401_Capstone_PV_Prediction_V001_SHORTCUT.md
```

사용자가 "캡스톤디자인"을 떠올려 `050_Projects/`로 이동하면 -> 바로가기 -> 본문
사용자가 "AI 기술"을 떠올려 `500_Technology/`로 이동하면 -> 바로가기 -> 본문
사용자가 "논문"을 떠올려 `010_Verified/`로 이동하면 -> 본문 직접 접근

### 3-4. 바로가기 자동 생성 규칙

인제스트 시 Claude가 자동 판단:
1. 정본 위치 결정 (가장 핵심적인 분류)
2. 관련 분류 식별 (2-3개)
3. 각 관련 분류에 바로가기 문서 자동 생성
4. index.md에 정본은 일반 등록, 바로가기는 `[S]` 표시

---

## 4. 최종 폴더 구조

```
001_Wiki_AI/
  CLAUDE.md                      Schema v3
  index.md                       카탈로그 (정본 + 바로가기 구분)
  log.md                         연산 이력

  --- Raw Layer (불변) ---
  000_Raw/                       수동 투입 원본
  Clippings/                     Obsidian Web Clipper

  --- 신뢰도/출처 계층 (축 2) ---
  010_Verified/                  정식 발행 문서 (책, 논문, 특허, 교재)
  020_Official/                  공적 기관 자료 (과기부, 행안부, 교육부, 법령)
  030_Work/                      업무 산출물 (계획서, 보고서, 회의록)
  040_Correspond/                공문/메일 (공식 수발신)
  050_Projects/                  개인 프로젝트 (캡스톤, 과제, 실험)
  060_Media/                     영상/미디어 (YouTube, 강의, 팟캐스트)
  070_WebClip/                   비정형 웹 스크랩 (블로그, 나무위키)

  --- KDC 주제 분류 (축 1) ---
  001_General/                   총류
  100_Philosophy/                철학
  200_Religion/                  종교
  300_Social_Science/            사회과학/행정/교육
  400_Natural_Science/           자연과학
  500_Technology/                기술과학/AI/에너지
  600_Arts/                      예술
  700_Language/                  어학
  800_Literature/                문학
  900_History/                   역사

  --- 메타 ---
  990_Meta/                      위키 메타
```

각 폴더 하위: `entities/` `concepts/` `sources/` `analysis/`

---

## 5. 프론트매터 v3 (3축 반영)

```yaml
---
title: "태양광 발전량 예측 AI 모델"
domain: 500_Technology             # 축 1: 주제
reliability: 010_Verified          # 축 2: 신뢰도/출처
type: source
created: 2026-04-01
updated: 2026-04-10
sources: []
tags: [AI, 태양광, 캡스톤디자인, PV-prediction]
context:                           # 축 3: 맥락
  project: "260401_캡스톤디자인"
  area: "에너지신산업실"
  status: active
shortcuts:                         # 바로가기 목록
  - 050_Projects/sources/260401_Capstone_PV_Prediction_V001_SHORTCUT.md
  - 500_Technology/sources/260401_Capstone_PV_Prediction_V001_SHORTCUT.md
---
```

---

## 6. 인제스트 워크플로우 v3

```
0. 사전 점검 (기존과 동일)
1. 원본 읽기 (기존과 동일)
2. 3축 분류 판정 (신규)
   a. 축 1 (주제): KDC 어디에 해당하는가?
   b. 축 2 (신뢰도): 010~070 중 어디인가?
   c. 축 3 (맥락): 어떤 프로젝트/업무 영역과 관련되는가?
3. 정본 위치 결정
   - 신뢰도 계층(010~070) 중 가장 핵심적인 곳 = 정본
   - 또는 주제 분류(KDC) 중 가장 핵심적인 곳 = 정본
   - 판단 기준: "이 자료의 정체성은 무엇인가?" (논문이면 010, 프로젝트 결과면 050)
4. 정본 페이지 생성 (기존과 동일)
5. 바로가기 문서 생성 (신규)
   - 관련 분류 2-3곳에 SHORTCUT.md 자동 생성
   - 사용자에게 바로가기 위치 확인 요청
6. index.md 갱신 (정본 [C] + 바로가기 [S] 구분)
7. log.md 기록
```

---

## 7. YAGNI Review

### 첫 버전에 포함

- 010_Verified (이미 구현)
- 020_Official ~ 070_WebClip 신뢰도 폴더 생성
- 바로가기 문서 시스템 (SHORTCUT.md 형식 + 인제스트 시 자동 생성)
- 프론트매터 v3 (reliability + context + shortcuts 필드)
- index.md에 [C]정본 / [S]바로가기 구분

### 향후 확장 (첫 버전 미포함)

- Dataview 자동 MOC (Obsidian 플러그인 연동)
- 바로가기 자동 검증 (정본 삭제 시 바로가기 고아 감지)
- 신뢰도 자동 판정 (URL 패턴으로 020_Official vs 070_WebClip 자동 분류)
- 통제 어휘(Controlled Vocabulary) 시스템 (태그 일관성 강제)

---

## 8. 구현 순서

| 단계 | 작업 |
|:---:|:---|
| 1 | 020_Official ~ 070_WebClip 폴더 생성 (각 4개 하위 폴더) |
| 2 | CLAUDE.md v3 업데이트 (3축 분류 + 바로가기 규칙) |
| 3 | SKILL.md 업데이트 (인제스트 v3 워크플로우 + SHORTCUT 생성) |
| 4 | index.md v3 (Reliability 컬럼 + [C]/[S] 표시) |
| 5 | 기존 8개 페이지에 reliability 프론트매터 추가 |
| 6 | wiki-lint.js에 바로가기 검증 추가 (정본 존재 여부 확인) |
| 7 | 검증: 캡스톤 논문 시나리오로 전체 워크플로우 테스트 |

---

## 9. Brainstorming Log

| Phase | 결정 | 근거 |
|---|---|---|
| Phase 1 | 지식 구조/분류 부족이 핵심 문제 | 사용자 선택 |
| Phase 1 | 도메인 + 하위 구조 둘 다 재설계 | 사용자 선택 |
| Phase 2 | KDC 하이브리드 채택 | 검증된 국가 표준 + 신뢰도 계층 이중 분류 |
| Phase 3 | 첫 버전에 KDC 전체 분류 생성 | 사용자 선택 |
| Research | 교차 분류 -> MOC + Canonical + Shortcut 패턴 | Deep Research: 아키비스트 전통 + Nick Milo LYT |
| Research | 신뢰도 -> Admiralty Code 간소화 (010~070) | Deep Research: NATO 6x6 -> 7단계 간소화 |
| Research | 3축 분류 (주제 + 신뢰도 + 맥락) | Deep Research: 기존에 3축 결합 체계 없음 -> 신규 설계 |

---

## Next Step

사용자 승인 후: `/pdca design wiki-v3-upgrade`
