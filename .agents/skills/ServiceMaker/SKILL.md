---
name: ServiceMaker
description: "체계적인 스킬 개발 방법론. 새로운 스킬을 만들 때 9단계 표준 시퀀스를 강제하여 무결점 스킬을 개발합니다. '스킬 만들어줘', 'ServiceMaker', '새 기능 개발' 키워드 시 트리거됩니다."
---

# ServiceMaker (무결점 스킬 빌더)

새로운 스킬을 개발할 때 반드시 따라야 할 **9단계 표준 시퀀스**입니다.

보조 스크립트: `scripts/scaffold_watcher.py`

---

## 9단계 Standard Sequence

### Step 0: 체크포인트 확인
bkit PDCA 상태 확인 및 현재 세션 스냅샷 저장:
```bash
# bkit 상태 확인
/pdca status
```

### Step 1: PDCA 기획
```
/pdca pm [스킬명]    → PM 분석
/pdca plan [스킬명]  → 계획 문서 생성
```

### Step 2: 디렉토리 초기화
```
.agents/skills/[스킬명]/
├── SKILL.md
├── scripts/
└── Log/
```

### Step 3: Watcher 설정
`scaffold_watcher.py`로 개발 중 파일 변경 감시:
```bash
python scripts/scaffold_watcher.py --skill [스킬명] --watch
```

### Step 4: ZAF 프롬프트 엔지니어링
Zero-AI Footprint 원칙을 적용한 핵심 프롬프트 설계:
- AI 생성 흔적(기계적 표현, 과도한 이모지) 배제
- 구체적인 입출력 명세
- 에러 핸들링 규칙 명시

### Step 5: 핵심 구현
- Watcher 게이트 상태를 주기적으로 확인하며 구현
- Python 스크립트의 경우 `asyncio` 비동기 패턴 권장
- 의존성은 `requirements.txt`에 명시

### Step 6: E2E 테스트
```bash
python tests/test_e2e.py
```

### Step 7: SKILL.md 완성 + 자기치유 프로토콜
- description frontmatter에 트리거 키워드 명시
- 버그 이력 로그 섹션 포함
- 자동 업데이트 트리거 조건 명시

### Step 8: Navigator 생성
`Mermaid_FlowChart` 스킬로 실행 흐름도 생성:
- 각 Phase/Step을 노드로 표현
- 에러 분기 포함

### Step 9: 시스템 등록 (CLAUDE.md 직접 갱신)

`${PROJECT_ROOT}/CLAUDE.md`의 **스킬 트리거 테이블**에 직접 등록:

1. SKILL.md 전문 확인 — 이름, 유형, 실제 기능 목록 파악
2. 트리거 테이블 행 추가:
   ```
   | 트리거 키워드 | `스킬명` | 설명 |
   ```
3. Tier-A 스킬인 경우 — `Mermaid_FlowChart` 스킬로 Navigator.md 생성 후 등록
4. 등록 완료 후 레거시 패턴 잔류 확인:
   ```bash
   grep -r "Total_SystemRun\|@\[/\|003_AI_Project" .agents/ --include="*.md"
   # → 0건이어야 정상
   ```

---

## 핵심 원칙

- **Step 순서 절대 준수**: 건너뛰기 금지
- **Watcher Gate**: Step 5 구현 중 수시로 확인
- **자기치유 필수**: 개발 중 발견한 버그는 SKILL.md에 즉시 기록
