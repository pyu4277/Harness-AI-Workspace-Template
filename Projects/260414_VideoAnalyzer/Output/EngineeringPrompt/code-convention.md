# 코딩 규칙 -- VideoAnalyzer

> 개발 표준 정의서(docs/05)의 요약. 실제 구현 시 이 파일을 참조한다.

## 네이밍

| 대상 | 규칙 | 예시 |
|------|------|------|
| 파일 | `NN_동사_목적어.py` | `01_extract_frames.py` |
| 함수 | `snake_case` | `extract_frames()` |
| 변수 | `snake_case` | `frame_interval` |
| 클래스 | `PascalCase` | `SceneSegmenter` |
| 상수 | `UPPER_SNAKE` | `SSIM_THRESHOLD` |
| 설정 키 | `snake_case` | `"frame_interval": 0.5` |
| 출력 파일 | `YYMMDD_[이름]_[태그]` | `260414_변압기강의_AI분석보고서.md` |

## 필수 패턴

```python
# 파일 헤더
"""VideoAnalyzer Pipeline - Stage N: [Stage명]
흡수 출처: TransTest/pipeline/0N_xxx.py 개량 (Reference-Port)"""

# 인코딩 안전
subprocess.run(cmd, capture_output=True, text=True, errors="replace")

# 파일 I/O
open(path, encoding="utf-8")

# 경로
Path(__file__).parent  # 절대경로 하드코딩 금지
```

## 금지 패턴

- `eval()`, `exec()`, `import *`
- 절대경로 문자열 (`"C:/Users/..."`)
- `subprocess` without `errors="replace"`
- `open()` without `encoding="utf-8"`
- config.json 값 하드코딩

## 커밋

```
feat(extract): 프레임 추출 스크립트 구현
fix(sync): SSIM 계산 프레임 크기 불일치 수정
docs(arch): 아키텍처 설계서 갱신
```
