# 스킬 카탈로그

> 005_AI_Project에서 사용 가능한 스킬, 트리거, 커맨드 전체 목록.

---

## 자동 트리거 스킬

| 트리거 조건 | 스킬 | 동작 |
|---|---|---|
| "hwpx", "한글 문서", "hwp", ".hwpx" 언급 | `HWPX_Master` | Track A/B/C/D 자동 판별 후 실행 |
| ".pdf", ".docx", ".pptx", "Word", "워드", "PowerPoint", "발표자료" 언급 | `DocKit` | PDF/DOCX/PPTX 포맷 자동 판별 후 처리 |
| "논문", "학술", "RISS", "학술 검색" | `PaperResearch` | RISS + 구글 학술 자동 검색 |
| 에러 반복 감지, "에러 분석", "오류 복구" | `auto-error-recovery` | RCA -> 복구 루프 (최대 3회) |
| "프롬프트 만들어줘", "프롬프트 변환", "예시 만들어줘" | `PromptKit` | 프롬프트 변환(4단계) + 예시 자동 생성(Step 5) |
| "흐름도", "순서도", "다이어그램" | `Mermaid_FlowChart` | ELK 렌더러 Mermaid 생성 |
| "파일명 정리", "파일 이름 바꿔줘" | `FileNameMaking` | 시맨틱 평가 후 일괄 변경 |
| "스크린샷", "화면 캡처", "에러 캡처" | `VisualCapture` | 캡처 + 주석 + Vision 분석 보고서 |
| "전문용어 정리", "용어 추가" | `term-organizer` | 용어사전.md 관리 |
| 세션 종료, "저장해줘", "핸드오프", "/handoff" | `session-handoff` | 지식 증류 + 로그 저장 |
| "스킬 만들어줘", "ServiceMaker" | `ServiceMaker` | 9단계 개발 + CLAUDE.md 자동 등록 |
| "마크다운 검사", "md 오류", "mdGuide" | `mdGuide` | Zero-Defect MD 린팅 |
| "하네스", "프로젝트 초기화", "harness" | `harness-architect` | 하네스 4기둥 프로젝트 초기화 |

## bkit 로컬 스킬

| 스킬명 | 경로 | 용도 |
|:---|:---|:---|
| `pdca` | `.agents/skills/pdca/` | PDCA 전체 주기 관리 |
| `bkit-rules` | `.agents/skills/bkit-rules/` | 코어 규칙 (레벨 감지, 자동 트리거) |
| `bkit-templates` | `.agents/skills/bkit-templates/` | PDCA 문서 템플릿 |
| `plan-plus` | `.agents/skills/plan-plus/` | 브레인스토밍 강화 기획 |
| `development-pipeline` | `.agents/skills/development-pipeline/` | 9단계 개발 파이프라인 |
| `code-review` | `.agents/skills/code-review/` | 코드 품질 분석 |
| `zero-script-qa` | `.agents/skills/zero-script-qa/` | Docker 로그 기반 QA |
| `btw` | `.agents/skills/btw/` | 개선 제안 수집 |

## PDCA 커맨드 (채팅창 슬래시 커맨드)

```
/pdca pm <기능명>       PM 에이전트 팀 분석
/pdca plan <기능명>     계획 문서 생성
/pdca design <기능명>   설계 문서 생성
/pdca do <기능명>       구현 가이드
/pdca analyze <기능명>  갭 분석
/pdca iterate <기능명>  자동 개선 반복
/pdca report <기능명>   완료 보고서
/pdca archive <기능명>  완료된 기능 아카이브
/pdca cleanup           아카이브 정리
/pdca status            현재 PDCA 상태
/pdca next              다음 단계 가이드
/plan-plus <기능명>     브레인스토밍 강화 기획
/code-review <경로>     코드 품질 분석
/zero-script-qa         Docker 로그 기반 QA
/simplify               변경된 코드 품질 개선
/btw <제안>             개선 제안 즉시 수집
/development-pipeline   9단계 개발 파이프라인 가이드
```

## PDCA-도메인 스킬 연동 매핑

| PDCA 단계 | 도메인 스킬 | 트리거 조건 |
|:---|:---|:---|
| Plan | `PaperResearch` | 학술 연구/문헌 조사 포함 시 |
| Plan | `term-organizer` | 새 용어 발견 시 용어사전 업데이트 |
| Design | `Mermaid_FlowChart` | 아키텍처/워크플로우 시각화 필요 시 |
| Design | `PromptKit` | AI 파이프라인/프롬프트 설계 포함 시 |
| Do | `HWPX_Master` | 산출물이 한글 문서 형식 시 |
| Do | `DocKit` | 산출물이 Word/PowerPoint/PDF 형식 시 |
| Check | `mdGuide` | 마크다운 문서 품질 검증 |
| Report | `session-handoff` | 세션 로그/지식 증류 |

## 스킬 Tier 분류

| Tier | 스킬 목록 | 특징 |
|:---|:---|:---|
| Tier-A (스크립트 포함) | HWPX_Master, DocKit, PaperResearch, VisualCapture, session-handoff, auto-error-recovery, ServiceMaker | Navigator.md 필수 |
| Tier-B (순수 프롬프트) | PromptKit, Mermaid_FlowChart, FileNameMaking, mdGuide, term-organizer | SKILL.md 인라인 |
| Tier-C (bkit 프레임워크) | pdca, bkit-rules, bkit-templates, plan-plus, development-pipeline, code-review, zero-script-qa, btw | bkit 런타임 연동 |
| Tier-S (하네스 메타) | harness-architect | 프로젝트 하네스 설계 |
