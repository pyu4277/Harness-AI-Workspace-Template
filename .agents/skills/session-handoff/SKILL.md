---
name: session-handoff
description: "대화 내역(Context)을 분석하여 지식을 증류하고, 개별 프로젝트 Log 폴더 및 통합 1st_Log 대시보드에 기록합니다. 세션 전환 시 문맥을 유지(Warm Boot)하게 합니다. '저장해줘', '핸드오프', '세션 저장', '/handoff' 키워드 시 트리거됩니다."
version: 2.1.0
---

# Session Handoff (지식 증류 + 세션 로깅)

대화 기록 소실 방지를 위한 **지식 증류(Knowledge Distillation)**, **로그 동기화**를 수행하는 단일 진입점 스킬입니다.

---

## 파일 관리 체계

```
004_AI_Project/
├── Projects/
│   └── YYMMDD_ProjectName/
│       └── Log/
│           └── session_YYMMDD_HHMM.md   ← 개별 세션 로그
└── docs/
    └── LogManagement/
        └── 1st_Log.md                   ← 통합 대시보드 (500줄 초과 시 아카이브 분할)
```

---

## 핵심 임무

1. **지식 증류**: 시행착오 과정을 제거하고 "Goal / Actions / Result / Next Steps" 4요소만 추출.
2. **Q&A 히스토리 보존**: 대화 쌍(Turn)이 병합되거나 유실되지 않도록 개별 묶음으로 보존.
3. **개별 분산 저장**: 프로젝트 하위 `Log/` 폴더에 `session_YYMMDD_HHMM.md`로 저장.
4. **통합 동기화**: `docs/LogManagement/1st_Log.md` 상황판을 하이퍼링크로 업데이트.

---

## 트리거 조건

| 트리거 | 키워드 | 실행 모드 |
|:------|:------|:---------|
| 명시적 세션 저장 | `저장해줘`, `세션 저장`, `핸드오프`, `/handoff` | Full handoff |
| 로그 추가 | `기록해줘`, `로그에 추가해줘`, `이거 남겨줘` | Log append only |
| 자율 판단 | 작업이 완료되었거나 세션 전환이 명확할 때 | Full handoff |

---

## 실행 파이프라인

### Phase 1: Context Analysis (지식 증류)

1. 대화 전체를 분석하여 현재 작업이 어느 프로젝트에 귀속되는지 특정.
2. Goal / Actions / Result / Next Steps 4요소 도출.
3. 대화의 Q&A 쌍을 `<details><summary>` 형식으로 정리하여 임시 파일 생성.

### Phase 2 & 3: Python 자동화 실행

지식 증류 완료 후 AI가 직접 `1st_Log.md`를 수정하지 말고, 반드시 `scripts/handoff.py`를 호출:

```bash
python ".agents/skills/session-handoff/scripts/handoff.py" \
  "${PROJECT_ROOT}/Projects/YYMMDD_이름" \
  "<Goal>" \
  "<Actions>" \
  "<Result>" \
  "<Next Steps>" \
  "<QA_History_임시파일경로>"
```

- `${PROJECT_ROOT}` = CLAUDE.md가 위치한 폴더 (절대경로 하드코딩 금지 — 상대경로 사용)
- QA History는 임시 파일 경로로 전달 (Windows 명령어 길이 제한 방지)
- 스크립트가 자동으로: 개별 로그 생성 → 1st_Log.md 업데이트 → 500줄 초과 시 아카이브 분할

---

## 다중 프로젝트 분산 로깅

단일 세션에서 2개 이상의 프로젝트를 다뤘다면:

1. 각 Q&A 쌍을 프로젝트별로 매핑.
2. 프로젝트별 임시 파일 N개 생성.
3. `handoff.py`를 N번 순차 호출 (이전 호출 완료 확인 후 다음 호출).

**금지**: 서로 다른 프로젝트 내용을 하나의 로그에 병합하는 것.

---

## 제약 사항

- 파일 확장자는 `.md`로 통일.
- 절대경로 하드코딩 금지 — 링크는 현재 파일 기준 상대경로로 작성.
- log-this 기록 시 사용자 입력 원문 보존 우선.
