# 세션 프로토콜

> 세션 시작(Warm Boot)과 종료(Handoff) 절차. 2026-04-11부터 `llm-wiki` 스킬이 session-handoff 기능을 통합 흡수.

---

## Warm Boot (세션 시작 시 의무)

새 대화 세션이 시작되면 다음 순서로 컨텍스트를 복원한다:

1. **`.harness/next-session.md`** -- 가장 먼저. 다음 세션 진입점 (IMP-018).
2. **`docs/LogManagement/1st_Log.md`** -- 시간순 대시보드. 최근 세션의 Next Steps 확인.
3. **`001_Wiki_AI/`** -- 재사용 가능한 개념/지식 정본 (선택적).

---

## 세션 종료 (llm-wiki 통합 방식)

**2026-04-11부터 구 `session-handoff` 스킬은 `llm-wiki ingest`에 완전 편입됨**. 세션 종료 시 하나의 호출로 3중 백업이 완성된다.

### 트리거 키워드

다음 중 하나로 llm-wiki의 세션 핸드오프 경로가 자동 활성화:
- `저장해줘`, `핸드오프`, `handoff`, `세션 저장`
- `기록해줘`, `지식화`, `대화 저장`
- `체크포인트`, `Warm Boot`, `next-session`
- `wiki ingest` + Mode 2/3 선택

### Mode Selector (진입 시 번호 선택)

```
어떤 작업을 수행할까요?
1) Source only -- 원본 파일 인제스트만 (기존 방식)
2) Session handoff only -- 대화 증류 + 로그 + 1st_Log + next-session
3) Both (권장) -- 위키 지식화 + 세션 핸드오프 동시 수행
```

### Mode 2 / 3 흐름

```
llm-wiki ingest (Mode 2 또는 3)
    |
Phase A: Context Analysis (Goal / Actions / Result / Next Steps 4요소 증류)
    |
(Mode 3만) Phase A+: 재사용 개념 후보 3-5개 식별 + Mode 1 Phase 1~6 (위키 concepts/sources 생성)
    |
Phase B: handoff.py 호출 (node 우선, python 대체)
  → Projects/YYMMDD_*/Log/session_YYMMDD_HHMM.md (개별 로그)
  → docs/LogManagement/1st_Log.md (통합 대시보드)
  → 500줄 초과 시 docs/archive/로 자동 분할
    |
Phase C: .harness/next-session.md 갱신 (IMP-018)
  → atomicWriteWithBackup으로 .bak 자동 백업
    |
Phase D: 완료 보고 + .tmp/qa_*.md 정리
```

## 로그 관리 규칙

- **AI가 `1st_Log.md`를 직접 편집하지 않음** -- 반드시 `handoff.py` 경유
- **스크립트 경로**: `.agents/skills/llm-wiki/scripts/handoff.py`
- **Python PATH 미보장 환경(IMP-002)**: AI가 handoff.py 로직을 Write 도구로 직접 재현하는 폴백 사용
- **다중 프로젝트**: 프로젝트별로 handoff.py를 순차 호출 (병렬 금지, 1st_Log 쓰기 경쟁 방지)
- **다중 프로젝트 내용을 하나의 로그에 병합 금지**

### handoff.py 호출 예

```bash
# node 우선 시도
node -e "require('child_process').execSync('python .agents/skills/llm-wiki/scripts/handoff.py \"Projects/YYMMDD_이름\" \"<Goal>\" \"<Actions>\" \"<Result>\" \"<Next>\" \"<QA임시파일>\"', {stdio:'inherit'})"

# 또는 직접
python ".agents/skills/llm-wiki/scripts/handoff.py" \
  "Projects/YYMMDD_이름" "<Goal>" "<Actions>" "<Result>" "<Next>" "<QA임시파일>"
```

## 파일 위치

- `.harness/next-session.md` -- 다음 세션 진입점 (IMP-018)
- `docs/LogManagement/1st_Log.md` -- 통합 시간순 대시보드
- `Projects/YYMMDD_*/Log/session_YYMMDD_HHMM.md` -- 개별 프로젝트 로그
- `docs/archive/1st_Log_archived_*.md` -- 500줄 초과 시 자동 생성
- `001_Wiki_AI/500_Technology/concepts/*` -- Mode 3 재사용 개념 (선택)
- `001_Wiki_AI/500_Technology/sources/YYMMDD_*.md` -- Mode 3 세션 전체 기록

## 관련 스킬

| 스킬 | 역할 | 트리거 |
|------|------|--------|
| `llm-wiki` | 지식 관리 + 세션 핸드오프 통합 | 위키/저장/핸드오프/지식화 키워드 |
| `harness-imprint` | 각인 기록 (세션 중 발견된 실수/재시도) | `/imprint record` |
| `term-organizer` | 전문용어 사전 갱신 | Mode 1/3 Phase 7에서 자동 연계 |

## 폐지 (Deprecated)

- **구 `session-handoff` 스킬** -- 2026-04-11 폐지. `llm-wiki ingest --mode=handoff` 또는 `--mode=both` 사용.
- `.agents/skills/session-handoff/` 디렉토리 삭제됨.
- 핵심 스크립트 `handoff.py`는 `.agents/skills/llm-wiki/scripts/handoff.py`로 이동되어 보존.
