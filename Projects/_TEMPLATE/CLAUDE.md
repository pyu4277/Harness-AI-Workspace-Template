# [프로젝트명] — 프로젝트 컨텍스트

> 이 파일은 이 프로젝트 폴더에서 Claude Code를 실행할 때 자동으로 로드됩니다.
> 루트 CLAUDE.md의 거버넌스를 상속하며, 프로젝트별 규칙을 추가합니다.

## 프로젝트 개요

- **목적**: [프로젝트 목적 한 줄 설명]
- **시작일**: YYYY-MM-DD
- **상태**: 진행 중 / 완료 / 보류
- **주요 출력물**: [예: HWPX 보고서, Python 스크립트, Excel 분석 결과]
- **관련 스킬**: [이 프로젝트에서 주로 사용하는 스킬. 예: HWPX_Master, DocKit, PaperResearch]

## 핵심 파일 구조

```
YYMMDD_ProjectName/
├── CLAUDE.md              ← 이 파일
├── requirements.txt       ← Python 의존성
├── .env                   ← API 키 (gitignore 필수, 절대 커밋 금지)
├── Log/                   ← session_YYMMDD_HHMM.md 자동 저장
├── Input/
│   ├── raw/               ← 미가공 원본 (PDF, HWPX, 이미지 등)
│   ├── data/              ← 정형 데이터 (CSV, Excel, JSON)
│   ├── refs/              ← 참고·기준 문서 (평가 기준, 가이드라인)
│   └── captures/          ← 화면 캡처·스크린샷 (VisualCapture 스킬)
├── Output/
│   ├── draft/             ← 초안 (검토·수정 중)
│   ├── final/             ← 최종 확정본 (제출·배포용)
│   └── archive/           ← 구버전 보관
├── src/
│   ├── agents/            ← AI 파이프라인·에이전트 스크립트
│   ├── utils/             ← 공통 유틸리티 함수
│   └── tests/             ← 테스트 코드
└── docs/
    ├── plan/              ← 기획·설계 노트
    └── notes/             ← 회의록·메모·결정 사항
```

## 하위 폴더 사용 기준

| 폴더 | 넣는 파일 |
|:---|:---|
| `Input/raw/` | 처음 받은 그대로의 원본 파일 |
| `Input/data/` | 분석 가능한 정형 데이터 |
| `Input/refs/` | 기준 문서, 가이드라인, 평가 지표 |
| `Input/captures/` | 화면 캡처·스크린샷 원본 및 주석본 |
| `Output/draft/` | 검토 요청 전 초안 |
| `Output/final/` | 최종 확정·제출 버전 |
| `Output/archive/` | 덮어쓰기 전 구버전 |
| `src/agents/` | 파이프라인·자동화 스크립트 |
| `src/utils/` | 재사용 가능한 공통 함수 |
| `src/tests/` | 검증·무결성 테스트 코드 |
| `docs/plan/` | 기획서, 설계 노트 |
| `docs/notes/` | 회의록, 메모, 결정 기록 |

## 프로젝트별 규칙

- [이 프로젝트에 특화된 규칙이 있으면 여기에 추가]
- [예: "출력은 반드시 HWPX 형식으로", "평가 기준은 Input/refs/기준문서.pdf 참조"]

## 의존성 메모

- [특이한 설치 요구사항, 버전 제약 등]
- [예: "한글 5.0 이상 설치 필수 (Track D 사용 시)", "Python 3.10 이상"]
