"""
analyze.py — 이미지 분석 + 보고서 생성 스크립트

캡처 이미지를 Claude Vision API로 분석하여 마크다운 보고서를 생성합니다.

사용법:
  # 기본 분석 (에러/문제 파악)
  python analyze.py --input capture.png --out "Output/draft/에러분석.md"

  # 분석 목적 지정
  python analyze.py --input capture.png \
      --prompt "이 화면에서 발생한 오류의 원인과 해결 방법을 분석해줘." \
      --out "Output/draft/에러분석.md"

  # 주석 이미지 + 여러 이미지 비교 분석
  python analyze.py --input before.png after.png \
      --prompt "두 화면의 차이점을 설명해줘." \
      --out "Output/draft/비교분석.md"

의존성: pip install anthropic Pillow
환경변수: ANTHROPIC_API_KEY (.env 파일에 저장)
"""

import argparse
import base64
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import anthropic
    from PIL import Image
except ImportError:
    print("[ERROR] 필수 패키지 없음. 설치: pip install anthropic Pillow", file=sys.stderr)
    sys.exit(1)


DEFAULT_PROMPT = (
    "이 화면 캡처 이미지를 분석해줘.\n"
    "1. 현재 상태 또는 오류 상황을 설명해줘.\n"
    "2. 문제가 있다면 원인을 진단해줘.\n"
    "3. 해결 방법 또는 다음 단계를 제안해줘.\n"
    "한국어로 답변해줘."
)


def load_env():
    """프로젝트 루트 또는 현재 디렉토리의 .env에서 API 키 로드"""
    from pathlib import Path
    for env_path in [Path(".env"), Path(__file__).resolve().parents[3] / ".env"]:
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        os.environ.setdefault(key.strip(), val.strip())
            break


def encode_image(path: Path) -> tuple[str, str]:
    """이미지를 base64로 인코딩하고 미디어 타입 반환"""
    suffix = path.suffix.lower()
    media_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                 ".gif": "image/gif", ".webp": "image/webp"}
    media_type = media_map.get(suffix, "image/png")
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8"), media_type


def analyze_images(image_paths: list[Path], prompt: str) -> str:
    """Claude Vision API로 이미지 분석"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY 없음. 프로젝트 .env 파일 확인.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    content = []
    for img_path in image_paths:
        data, media_type = encode_image(img_path)
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": data}
        })
    content.append({"type": "text", "text": prompt})

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": content}]
    )
    return response.content[0].text


def build_report(image_paths: list[Path], analysis: str, prompt: str) -> str:
    """마크다운 보고서 작성"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# Visual Capture 분석 보고서",
        f"",
        f"**생성일시**: {ts}",
        f"",
        f"---",
        f"",
        f"## 분석 대상 이미지",
        f"",
    ]
    for p in image_paths:
        rel = p.name
        lines.append(f"- `{rel}`")

    lines += [
        f"",
        f"---",
        f"",
        f"## 분석 요청",
        f"",
        f"> {prompt.replace(chr(10), chr(10) + '> ')}",
        f"",
        f"---",
        f"",
        f"## Claude 분석 결과",
        f"",
        analysis,
        f"",
        f"---",
        f"",
        f"*VisualCapture 스킬로 자동 생성*",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="이미지 분석 + 보고서 생성")
    parser.add_argument("--input", nargs="+", required=True, help="분석할 이미지 경로 (1개 이상)")
    parser.add_argument("--out", default=None, help="보고서 저장 경로 (.md). 미지정 시 이미지 폴더에 저장")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="분석 요청 프롬프트")
    args = parser.parse_args()

    load_env()

    image_paths = []
    for p in args.input:
        path = Path(p)
        if not path.exists():
            print(f"[ERROR] 파일 없음: {path}", file=sys.stderr)
            sys.exit(1)
        image_paths.append(path)

    print(f"[INFO] {len(image_paths)}개 이미지 분석 중...")
    analysis = analyze_images(image_paths, args.prompt)

    report = build_report(image_paths, analysis, args.prompt)

    if args.out:
        out_path = Path(args.out)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = image_paths[0].parent / f"analysis_{ts}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"[OK] 보고서 저장: {out_path}")


if __name__ == "__main__":
    main()
