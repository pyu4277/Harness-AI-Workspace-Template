---
name: mdGuide
description: "Zero-Defect 마크다운 검증 스킬. 마크다운 파일의 문법 오류를 검출하고 수정합니다. '마크다운 검사', 'md 오류', 'mdGuide', '마크다운 고쳐줘' 키워드 시 트리거됩니다."
---

# mdGuide — Zero-Defect 마크다운 규칙

마크다운 파일 작성 및 검증 시 반드시 준수해야 할 규칙 목록.

## 핵심 규칙 (Golden Rules)

| 규칙 ID | 내용 | 예시 |
|--------|------|------|
| MD001 | 제목 레벨은 순차적으로 증가 (H1→H2→H3) | H1 다음 바로 H3 금지 |
| MD009 | 줄 끝 후행 공백 제거 | `text ` → `text` |
| MD022 | 제목(Heading) 앞뒤 빈 줄 1개 필수 | `\n## 제목\n` |
| MD031 | 코드 블록 앞뒤 빈 줄 필수 | ` ```\n코드\n``` ` |
| MD032 | 리스트 앞뒤 빈 줄 필수 | |
| MD047 | 파일 끝에 개행 1개 필수 | 파일 마지막 줄 후 `\n` |

## 사용법

```
/mdGuide review [파일경로]   → 파일 검사 후 오류 목록 출력
/mdGuide fix [파일경로]      → 자동 수정 가능한 오류 수정
/mdGuide template [타입]     → 템플릿 생성 (readme / report / doc)
```

## 자동 적용 조건

- 새 마크다운 파일 생성 시 자동 검증
- PDCA 문서 (plan/design/report) 생성 완료 후 자동 검증
- `auto-error-recovery`의 Phase 4에서 보고서 작성 시 자동 적용
