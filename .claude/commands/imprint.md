---
description: 각인(imprint) 시스템 - 기록/조회/검색/통계/decay/archive/edit
argument-hint: "[record|list|search|stats|decay|archive|edit] [키워드|ID]"
user-invocable: true
---

# /imprint -- 각인 시스템 디스패처

구조화된 교훈(각인)을 관리한다. `harness-imprint` 스킬을 호출하는 슬래시 커맨드 진입점.

## 서브커맨드

| 명령 | 설명 |
|------|------|
| `/imprint record` | 현재 세션의 고투를 각인으로 기록 |
| `/imprint list` | 전체 각인 목록 (가중치순) |
| `/imprint search <키워드>` | 키워드로 각인 검색 |
| `/imprint stats` | 각인 통계 |
| `/imprint decay` | 수동 decay 체크 실행 |
| `/imprint archive` | 아카이브된 각인 목록 조회 |
| `/imprint edit <ID>` | 특정 각인 수정 (대화형) |

## 자동 동작

- 세션 시작 시 `imprint-session-start.js`가 자동으로 상위 10개 각인을 `active-imprints.md`로 로드
- 사용자 프롬프트 입력 시 `prompt-refiner.js`가 trigger_keywords 매칭 후 자동 리콜
- 30일 미리콜 + recall_count=0 각인은 세션 시작 시 자동 decay
- 12개 초과 시 최하위 weight 각인 자동 아카이브

## 관련 파일

- 스킬 정의: `.agents/skills/harness-imprint/SKILL.md`
- 각인 DB: `.harness/imprints.json`
- 아카이브: `.harness/imprints-archive.json` (자동 생성)
- 활성 각인: `.harness/active-imprints.md` (자동 생성)
- 변경 로그: `.harness/imprint-decay.log` (자동 생성)
- 세션 시작 훅: `.claude/hooks/imprint-session-start.js`
- 프롬프트 정제 훅: `.claude/hooks/prompt-refiner.js`

## 실행

이 커맨드는 `harness-imprint` 스킬을 호출한다. 서브커맨드와 인자는 스킬에 그대로 전달된다.
