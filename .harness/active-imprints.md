# Active Imprints (자동 생성 -- 직접 편집 금지)

> 가장 최근 + 가장 자주 회수된 각인. 세션 시작 시 imprint-session-start.js가 자동 갱신.
> 각인 = 기록보다 상위. 유사 상황 발생 시 자동으로 떠오르는 구조적 기억.

| ID | 심각도 | 원칙 | 트리거 키워드 |
|---|---|---|---|
| IMP-026 | high | llm-wiki Ingest 3 수준 분리: Level A (메타) / Level B (본문 발췌) / Level C (웹 접속). '지식화 완료' 주장은 Level B 이상일 때만. 대량 파일은 Top N 심화 + 나머지 카탈로그 | 메타 카탈로그, 깊이 분석, 지식화 완료, 바로가기 미접속 |
| IMP-024 | high | Windows + Python + 한글 출력 시 스크립트 시작부에 sys.stdout.reconfigure(encoding='utf-8') 선제 추가 필수. open() 에도 encoding='utf-8', errors='replace' 필수 | cp949, UnicodeEncodeError, 한글 출력, stdout 인코딩 |
| IMP-023 | high | 지식화 완료 직후 반드시 원본을 Raw → 990_Meta/archive 이동. wiki-pdf-stage archive-original 명령 사용. stage/extract/cleanup 3단계 후 명시적 4단계 archive 이동 필수 | 지식화 완료, archive 이동, IMP-017, Raw layer, 용량 그대로 |
| IMP-022 | high | 스킬 진화 시 신규 생성보다 기존 스킬 확장 우선. 파일 포맷 변환 스킬은 Convert-and-Archive 패턴 사용. Node.js fs.readdirSync withFileTypes.isFile() 한글 경로 불안정 → fs.statSync fallback | HWP, HWPX, Convert-and-Archive, 한컴, pywin32 |
| IMP-012 | critical | 다단계 파이프라인 스킬 호출 시 SKILL.md의 Phase를 1번부터 순서대로 100% 실행. 임의 단축/건너뛰기 금지. Decision Gate에서 반드시 사용자 승인 | harness-architect, 7단계, Phase |
| IMP-011 | critical | ECC 통합 시 반드시 minimal 프로필 유지. Harness 훅이 모든 Write/Edit/SessionStart의 최종 권한. ECC는 보충(block-no-verify, command-log, cost-tracker, Instinct)만 담당 | ECC, everything-claude-code, 통합 |
| IMP-010 | critical | 위키 정본 수정 시 반드시 shortcuts[] 확인 후 바로가기 동기화. 정본에 바로가기 경로 명기로 구조 깨져도 즉시 복구 가능. 바로가기에는 본문 금지 | 바로가기, shortcut, 정본 |
| IMP-007 | critical | 다단계 작업 완료 시 반드시 출력: (1) Feature Usage 요약 (2) 전문용어 등록 (3) 에러 각인. prompt-refiner.js가 자동 주입하므로 누락 시 하네스 위반 | 완료, 끝, done |
| IMP-027 | medium | Raw 폴더 용량 검증 시 .obsidian/ 등 숨김 디렉토리 무조건 제외 금지. 콘텐츠 용량 vs 설정 용량 분리 보고. 레거시 볼트 설정도 archive 이동 (영구 삭제 금지) | .obsidian, 레거시 설정, 숨김 폴더, 용량 남음 |
| IMP-025 | medium | Windows 장 경로 파일 (260+ 자) 처리는 Python 표준 API 대신 robocopy /MOV 사용. 파일명 생성 시 150자 이내 강제 | 장 경로, long path, WinError 3, robocopy |

> 총 29개 각인 중 상위 10개 표시. 전체 목록: /imprint list
>
> **2026-04-12 시스템 진화 추가 (6종)**: IMP-024 (Python cp949 인코딩) / IMP-025 (Windows 장 경로) / IMP-026 (Ingest 3 수준 분리) / IMP-027 (.obsidian 레거시) / IMP-028 (한컴 COM Quit 무해 오류) / IMP-029 (wiki-pdf-stage MAX_SIZE 동적 조정)
