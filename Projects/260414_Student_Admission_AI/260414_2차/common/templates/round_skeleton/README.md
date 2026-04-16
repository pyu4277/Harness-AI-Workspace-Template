# 회차 스켈레톤 (260414_N차)

회차 생성 시 이 폴더 또는 직전 회차 전체를 복제 후 `260414_N차` 로 리네임.

## 구조

```
260414_N차/
├── input/
│   ├── company_form.md        # 기업이 제공한 지원서 양식 원문
│   ├── job_description.md     # 직무기술서 원문
│   └── meta.json              # 기업명/직무/마감일/재지원 여부
├── company_profile.md         # D+3 템플릿 기반 작성
├── ideas.md                   # ideator 3+ 제안
├── output/
│   ├── 자소서.md
│   ├── 이력서.md
│   └── 포트폴리오.md
├── review_report.md           # reviewer 세션 결과
└── CHANGELOG.md               # 2차부터 필수
```

## 생성 절차

1. 프로젝트 루트에서 `cp -r 260414_{N-1}차 260414_N차`
2. `260414_N차/input/*` 기존 내용 삭제 후 신규 기업 자료 투입
3. `260414_N차/research_cache/*` 비움
4. `260414_N차/evidence_vault/0*/*` 안의 개별 증거 파일 비움 (INDEX.md 유지)
5. `260414_N차/CHANGELOG.md` 작성 (N>=2 필수)
6. 훅 자동 활성: 이전 회차 수정 시 `[WARN]` 발동 (프로젝트 루트 `.claude/hooks/pre_tool_guard.sh`)

## 패턴 주의

- 디렉토리 이름은 `260414_[0-9]+차` 고정 (한글 "차" 포함)
- 이전 회차 (N-1 이하) 는 archived. 수정 시 훅 경고
- 훅/설정은 프로젝트 루트 `.claude/` 1벌만 유지. 회차별 중복 금지
