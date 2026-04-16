# D+1. 회차 운영 설계서 (프로젝트 특수 요구)

"하위 프로젝트 구조를 바로 만들지 말고 1차/2차 폴더 안에 구조를 입힌다"는 요구에 대응.

## 하네스 엔지니어링 적용
| 기둥 | 역할 |
|------|------|
| 기둥1 | 회차 개념을 CLAUDE.md 최상단 정의 |
| 기둥2 | 이전 회차 쓰기 훅 차단 (불변성) |
| 기둥3 | 회차 경계를 경로 권한으로 물리 분리 |
| 기둥4 | 회차별 개선점이 차기 회차 구조에 자동 반영 |

## 1. 회차 생명주기

```
DRAFT → INPUT → RESEARCH → PROFILE → IDEATE → WRITE → REVIEW → FINAL → ARCHIVED
```

**ARCHIVED 이후**: 해당 회차 폴더는 읽기 전용. 모든 개선은 차기 회차에서만 반영.

## 2. 회차 생성 규칙

### 규칙 1: 단조 증가
- 회차 번호는 `max(기존 round_*) + 1`
- 삭제 후 재사용 금지 (archived 회차도 번호 점유)

### 규칙 2: 구조 상속
차기 회차는 다음 3단계로 구조 결정:
1. `common/templates/round_skeleton/` 복제 (기본 뼈대)
2. 최근 회차의 `CHANGELOG.md` 읽어 "구조 개선" 항목 자동 반영
3. 사용자 확인 → 개별 조정

### 규칙 3: 파일명/폴더명 고정
변경 가능한 것:
- meta.json 내용
- company_profile.md 내용
- ideas.md 내용
- output/* 내용

변경 불가한 것:
- 폴더명 (`input/`, `output/`, `company_profile.md` 등)
- 파일명 (`자소서.md`, `이력서.md`, `포트폴리오.md`)

## 3. 구조 개선 반영 프로토콜

### Case A: 국소 개선 (해당 회차만)
- round_N에서만 쓰는 임시 파일 추가 (예: `round_N/draft_notes.md`)
- CHANGELOG에 "국소" 태그로 기록
- common/에는 반영하지 않음

### Case B: 전역 개선 (모든 차기 회차 적용)
- common/templates/round_skeleton/ 업데이트
- common/CHANGELOG.md에 기록 (전역 이력)
- 차기 회차 생성 시 자동 상속

### Case C: 템플릿 개선 (자소서/이력서/포트폴리오 템플릿)
- common/templates/*.md 업데이트
- 기존 회차는 영향 없음 (불변성)
- 차기 회차만 새 템플릿 사용

## 4. 회차 간 비교 (품질 상승 확인)

```
회차 N 종료 시:
  1. round_N/review_report.md 스코어 집계
  2. round_(N-1)/review_report.md와 비교
  3. CHANGELOG.md에 "품질 변화" 섹션 추가
  4. 하락 시 원인 분석 필수
```

## 5. 동일 기업 재지원 처리

불합격 후 동일 기업 재지원:
1. round_N/meta.json의 `is_reapply: true` + `previous_round: [이전 회차 번호]`
2. 이전 회차 review_report.md + 합격 수기 대비 차이점 자동 리서치
3. 차이점이 CHANGELOG 상단 "개선 가설" 섹션에 기록
4. 가설 검증은 2주 후 (사용자 피드백 대기)

## 6. CHANGELOG.md 표준 형식

```markdown
# round_N CHANGELOG

## 개선 가설 (재지원 시)
- [가설 1]
- [가설 2]

## 구조 변경
### 국소 (round_N만)
- ...
### 전역 (common/ 반영)
- ...

## 프롬프트 개선
- [에이전트명]: [변경 내용]

## 품질 변화 (vs round_(N-1))
| 항목 | N-1 | N | 변화 |
|---|---|---|---|
| reviewer HIGH 건수 | ? | ? | ± |
| 근거 인용 수 | ? | ? | ± |

## 다음 회차 위한 권장 개선
- ...
```

## 7. 회차 폐기 처리

회차를 취소/폐기해야 할 경우:
- 폴더 삭제 금지 (번호 점유 유지)
- meta.json에 `status: "abandoned"` + `reason: "..."`
- output/ 파일은 빈 상태 허용
