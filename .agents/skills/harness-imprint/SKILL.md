---
name: harness-imprint
classification: workflow
classification-reason: "하네스 4기둥 피드백 루프의 핵심 메커니즘"
deprecation-risk: none
description: |
  작업 중 발생한 에러/재시도/고투를 구조화된 각인(Imprint)으로 기록하고,
  미래 세션에서 유사 상황 발생 시 자동으로 회수하는 진화하는 학습 시스템.

  기록(위키)과 각인의 차이: 기록은 찾아봐야 하고, 각인은 자동으로 떠오른다.

  Triggers: 각인, imprint, 교훈 기록, 이거 기억해, 교훈, lesson learned,
  각인 기록, 각인 검색, 각인 통계

  Do NOT use for: 단순 메모, 세션 로그(session-handoff 사용), 용어 정리(term-organizer 사용)
argument-hint: "[record|list|search|stats] [키워드]"
user-invocable: true
---

# Harness Imprint -- 진화하는 각인 시스템

> 실수는 기록이 아니라 각인이 되어야 한다. 기록은 찾아봐야 하고, 각인은 자동으로 떠오른다.

## 명령어

| 명령 | 설명 | 예시 |
|---|---|---|
| `/imprint record` | 현재 세션의 고투를 각인으로 기록 | `/imprint record` |
| `/imprint list` | 전체 각인 목록 (가중치순) | `/imprint list` |
| `/imprint search <키워드>` | 키워드로 각인 검색 | `/imprint search 인코딩` |
| `/imprint stats` | 각인 통계 | `/imprint stats` |

---

## record -- 각인 기록

현재 세션에서 발생한 고투를 증류하여 각인으로 기록한다.

### 절차

1. 세션의 대화 내용을 분석하여 아래 패턴을 감지한다:
   - 에러 메시지가 반복된 경우
   - 같은 파일을 3회 이상 수정한 경우
   - 접근 방식을 전환한 경우
   - 사용자가 "안 돼", "다시", "왜 안 되지" 등을 말한 경우

2. 감지된 각 고투에 대해 4요소를 추출한다:
   - **상황(situation)**: 무엇을 하려고 했는가
   - **고투(struggle)**: 무엇이 안 됐는가, 몇 번 시도했는가
   - **해결(resolution)**: 어떻게 해결했는가
   - **원칙(principle)**: 1문장으로 일반화한 교훈

3. 카테고리와 트리거 키워드를 자동 분류한다:
   - 카테고리: encoding, path-handling, environment, api-failure, permission, format, logic, performance
   - 키워드: 에러 메시지의 핵심 단어, 관련 기술명, 한국어 키워드

4. `.harness/imprints.json`에 새 각인을 추가한다:
   - ID: `IMP-{순번 3자리}` (예: IMP-004)
   - severity: critical/high/medium/low (반복 횟수와 영향도 기반)

5. 사용자에게 각인 요약을 보여준다.

### 각인 형식

```json
{
  "id": "IMP-004",
  "created": "2026-04-07T22:00:00Z",
  "category": "path-handling",
  "trigger_keywords": ["OneDrive", "공백", "경로", "space"],
  "situation": "OneDrive 경로에 한글+공백이 포함된 파일을 처리할 때",
  "struggle": "subprocess에서 경로가 잘려서 파일을 찾지 못함. 2회 실패",
  "resolution": "경로 전체를 따옴표로 감싸고 raw string 사용",
  "principle": "공백 포함 경로는 반드시 따옴표 + raw string",
  "severity": "high",
  "recall_count": 0,
  "last_recalled": null
}
```

---

## list -- 각인 목록

`.harness/imprints.json`에서 전체 각인을 가중치순으로 표시한다.

가중치 = severity 점수 * (1 + recall_count)

출력 형식:
```
전체 각인 목록 (가중치순)
---------------------------------
[IMP-002] critical | 회수 5회 | Windows에서 스크립트 런타임은 node 우선
[IMP-001] high     | 회수 3회 | 한글 레거시 파일은 cp949 + errors='replace'
[IMP-003] high     | 회수 1회 | bash + node -e 이스케이프 지옥 회피
---------------------------------
총 3개 각인, 9회 회수
```

---

## search -- 각인 검색

키워드로 trigger_keywords, situation, principle을 검색한다.

```
/imprint search 인코딩
→ [IMP-001] 한글 레거시 파일은 cp949 + errors='replace'가 기본값
  상황: HWP/CSV 등 한글 레거시 파일을 Python으로 읽을 때
  해결: encoding='cp949', errors='replace' 조합 사용
```

---

## stats -- 각인 통계

```
각인 통계
---------------------------------
총 각인 수: 12
총 회수 수: 47
카테고리별: encoding(3), path-handling(4), environment(2), api-failure(3)
가장 많이 회수된 각인: IMP-002 (15회)
가장 최근 각인: IMP-012 (2026-04-07)
---------------------------------
```

---

## 자동 메커니즘 (훅 연동)

이 스킬의 수동 명령 외에도 두 가지 자동 메커니즘이 작동한다:

1. **SessionStart 훅** (`imprint-session-start.js`):
   세션 시작 시 `.harness/active-imprints.md`를 자동 갱신. CLAUDE.md가 이 파일을 참조하므로 에이전트가 매 세션 상위 각인을 자동으로 인지.

2. **UserPromptSubmit 훅** (`imprint-prompt-match.js`):
   사용자 입력에서 trigger_keywords를 매칭. 매칭 시 `[각인 IMP-XXX] 원칙: ...`을 stderr로 출력하여 에이전트에게 즉시 알림. recall_count 자동 증가.

---

## 위키 vs 각인

| | 위키 (기존 AER/ADR) | 각인 (이 시스템) |
|---|---|---|
| 저장 | 분산 | 중앙 (imprints.json) |
| 회수 | 수동 (Read) | 자동 (키워드 매칭) |
| 강화 | 없음 | 회수될수록 가중치 상승 |
| 진화 | 정적 | 시간이 지날수록 정밀해짐 |
