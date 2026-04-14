# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## VideoAnalyzer -- AI 시각+텍스트 통합 영상 분석 파이프라인

영상을 프레임+자막으로 분해 -> 시각+텍스트 통합 분석 -> HWPX 보고서(이미지 삽입) 생성.
파이프라인: Extract -> Sync -> Analyze -> Importance Judge -> Report (docs/08_순서도및절차도.md 참조)

## 핵심 규칙

- 응답/보고서 한국어, 코드/변수/경로 영어
- 파일명: `YYMMDD_[이름]_[태그]` (예: `260414_변압기강의_AI분석보고서`)
- 분석 시 프레임 이미지 반드시 Read로 시각 분석 (텍스트만 분석 금지)
- 레퍼런스 수집 시 LLM 품질 검증 통과만 보고서 통합
- 보고서 출력: HWPX 형식 (python-hwpx), 중요 프레임 이미지 직접 삽입
- 이미지 아래 AI용 텍스트 설명서 필수 (구조/코드/Mermaid/학습포인트)
- 중요도 판별: importance_rules.json 규칙 엔진 (IN-01~03 포함, EX-01~03 제외)
- 자막 없으면 Whisper 자동 음성추출 (한국어 우선)
- 임계값/간격은 pipeline/config.json에서만 관리 (하드코딩 금지)
- subprocess 사용 시 `errors="replace"` 필수 (cp949 대응)
- 편집 전 반드시 Read로 실제 내용 확인
- 불확실하면 파일 확인 먼저, 없으면 사용자에게 질문

## 절대 금지

- eval(), new Function(), import *
- input/video/, workspace/frames/ 수정/삭제 (읽기 전용)
- .env 내용 노출/커밋, API Key 하드코딩
- 절대경로 하드코딩 (Path(__file__).parent 상대경로 사용)
- 새 패키지 무단 설치 (사용자 승인 필수)
- 텍스트만 보고 분석 완료 (시각 분석 누락)
- 품질 검증 없이 레퍼런스 통합

## 개발 환경

```bash
pip install opencv-python scikit-image Pillow numpy
pip install openai-whisper  # 자막 없는 영상용 (선택)
python pipeline/01_extract_frames.py  # Stage 1 실행
```

## 참조 문서

- 설계문서 8종: `docs/0[1-8]_*.md`
- 코딩 규칙: `code-convention.md`
- 아키텍처 결정: `adr.md`
- 파이프라인 설정: `pipeline/config.json`
- 중요도 규칙: `pipeline/importance_rules.json` (진화 가능 규칙 엔진)
- TransTest 참조: `C:\TransTest\pipeline\` (01_extract, 02_scene_segment 개량)

## 에이전트 운영

- 코드 작성과 코드 리뷰는 반드시 다른 에이전트
- 실수 발생 시 이 파일에 규칙 1줄 추가 (자기 진화)
- 구현 완료 후 컨텍스트 사용량 40% 이하 유지 권장
