# Active Imprints (자동 생성 -- 직접 편집 금지)

> 가장 최근 + 가장 자주 회수된 각인. 세션 시작 시 imprint-session-start.js가 자동 갱신.
> 각인 = 기록보다 상위. 유사 상황 발생 시 자동으로 떠오르는 구조적 기억.

| ID | 심각도 | 원칙 | 트리거 키워드 |
|---|---|---|---|
| IMP-002 | critical | Windows에서 스크립트 런타임은 node 우선. python은 PATH 보장 안 됨 | python, PATH, not found |
| IMP-001 | high | 한글 레거시 파일은 cp949 + errors='replace'가 기본값 | cp949, UnicodeDecodeError, 인코딩 |
| IMP-003 | high | bash + node -e 이스케이프 지옥 회피: 항상 별도 .js 파일 사용 | bash, node -e, 이스케이프 |

> 총 3개 각인 중 상위 3개 표시. 전체 목록: /imprint list