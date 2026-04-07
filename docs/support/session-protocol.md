# 세션 프로토콜

> 세션 시작(Warm Boot)과 종료(Handoff) 절차.

---

## Warm Boot (세션 시작 시 의무)

새 대화 세션이 시작되면 가장 먼저 `docs/LogManagement/1st_Log.md`를 읽어 이전 세션의 컨텍스트와 Next Steps를 인계받는다.

## 세션 종료 (Handoff)

모든 작업 종료 시 `session-handoff` 스킬 실행:

```
세션 전환/종료 감지 또는 "저장해줘" 입력
    |
session-handoff 트리거
    |
지식 증류: Goal / Actions / Results / Next Steps
    |
Projects/[프로젝트]/Log/session_YYMMDD_HHMM.md  -- 개별 로그
docs/LogManagement/1st_Log.md                    -- 통합 대시보드
```

## 로그 관리 규칙

- AI가 `1st_Log.md`를 직접 편집하지 않음
- 반드시 아래 스크립트 호출:

```bash
python ".agents/skills/session-handoff/scripts/handoff.py" \
  "${PROJECT_ROOT}/Projects/YYMMDD_이름" "<Goal>" "<Actions>" "<Result>" "<Next>" "<QA임시파일>"
```

- `1st_Log.md`가 500줄 초과 시 스크립트가 자동으로 `docs/archive/`로 분할
