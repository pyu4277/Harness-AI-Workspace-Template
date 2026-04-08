# Active Imprints (자동 생성 -- 직접 편집 금지)

> 가장 최근 + 가장 자주 회수된 각인. 세션 시작 시 imprint-session-start.js가 자동 갱신.
> 각인 = 기록보다 상위. 유사 상황 발생 시 자동으로 떠오르는 구조적 기억.

| ID | 심각도 | 원칙 | 트리거 키워드 |
|---|---|---|---|
| IMP-002 | critical | Windows에서 스크립트 런타임은 node 우선. python은 PATH 보장 안 됨 | python, PATH, not found |
| IMP-004 | high | 계획 수립 시 28종 설계문서 카탈로그에서 조건 기반 선별 후 사용자 승인. 전수 생성 금지 | 계획, 설계, plan |
| IMP-001 | high | 한글 레거시 파일은 cp949 + errors='replace'가 기본값 | cp949, UnicodeDecodeError, 인코딩 |
| IMP-003 | high | bash + node -e 이스케이프 지옥 회피: 항상 별도 .js 파일 사용 | bash, node -e, 이스케이프 |
| IMP-005 | high | 위키 경로는 항상 WIKI_ROOT(../001_Wiki_AI) 기준 상대경로. 절대경로 금지. guard 허용 목록에 등록 필수 | wiki, 위키, 001_Wiki_AI, WIKI_ROOT |
| IMP-006 | high | Obsidian CLI는 항상 Hybrid. 파일시스템 폴백 100% 보장. Obsidian 미실행 시 사용자 선택(켜기/그냥진행) 필수 | obsidian, CLI, vault, backlinks, orphans |
| IMP-007 | critical | 다단계 작업 완료 시 반드시: (1) Feature Usage 요약 (2) 전문용어 등록 (3) 에러 각인. prompt-refiner.js가 자동 주입 | 완료, 끝, done, finished |
| IMP-008 | high | 한국어 문자열 길이 판별 시 영어의 1/2~1/3 수준으로 임계값 설정. 단문=7자, 작업=10자 | 글자수, length, 임계값, 한국어 |
| IMP-009 | high | Obsidian CLI는 토글 ON + Register 버튼 클릭 2단계 필요. 터미널 재시작도 필수 | obsidian cli, PATH 등록, CLI 활성화 |

> 총 9개 각인 중 상위 9개 표시. 전체 목록: /imprint list