# 스킬 개발 가이드

> 새 스킬 개발 또는 설치 시 준수 사항.

---

## 개발 절차

1. `ServiceMaker` 스킬의 9단계 표준 절차 의무 준수
2. 개발 완료 후 `ServiceMaker` Step 9에 따라 CLAUDE.md 트리거 테이블 갱신
3. **Tier-A** (scripts 포함): `Mermaid_FlowChart` 흐름도 + `PromptKit Step 5` 다중 예시 -> `[스킬명]_Navigator.md` 생성 필수
4. **Tier-B** (순수 프롬프트): SKILL.md 인라인에 흐름도 + 최소 3개 예시 포함

## Tier 분류 기준

| Tier | 기준 | Navigator |
|:---|:---|:---|
| Tier-A | scripts/ 디렉토리 포함 | 별도 Navigator.md 필수 |
| Tier-B | 순수 프롬프트만 | SKILL.md 인라인 |
| Tier-C | bkit 프레임워크 연동 | bkit 문서 참조 |
| Tier-S | 하네스 메타 스킬 | knowledge/ 디렉토리 포함 |

## 레거시 패턴 점검

스킬 추가 후 반드시 확인:

```bash
grep -r "Total_SystemRun\|@\[/\|003_AI_Project\|GEMINI\.md" .agents/ --include="*.md"
# 0건이어야 정상
```

## SKILL.md 필수 front matter

```yaml
---
name: 스킬명
classification: workflow|domain|meta
description: |
  스킬 설명 (1-3줄)
  트리거 조건 명시
argument-hint: "사용법"
user-invocable: true|false
---
```
