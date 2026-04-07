"""
annotate.py — 이미지 주석·마킹 스크립트

캡처된 이미지에 시각적 마커(박스, 화살표, 텍스트, 하이라이트)를 추가합니다.

사용법:
  # 빨간 박스로 오류 영역 표시
  python annotate.py --input capture.png --box 100,200,400,350 --label "에러 발생 위치"

  # 노란 하이라이트
  python annotate.py --input capture.png --highlight 50,100,600,200

  # 화살표 추가 (시작x,시작y → 끝x,끝y)
  python annotate.py --input capture.png --arrow 300,100,300,250 --label "여기를 확인"

  # 텍스트만 삽입
  python annotate.py --input capture.png --text 50,50 --label "Step 1: 이 버튼 클릭"

  # 복합 주석 (박스 + 텍스트 + 화살표 동시)
  python annotate.py --input capture.png \
      --box 100,200,400,350 --label "오류 메시지" \
      --arrow 450,275,405,275 \
      --out "annotated_capture.png"

의존성: pip install Pillow
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[ERROR] Pillow 없음. 설치: pip install Pillow", file=sys.stderr)
    sys.exit(1)

# 색상 팔레트
COLOR_BOX = (220, 38, 38)       # 빨강 — 오류/중요
COLOR_HIGHLIGHT = (253, 224, 71, 120)  # 노랑 반투명 — 강조
COLOR_ARROW = (37, 99, 235)     # 파랑 — 흐름/방향
COLOR_TEXT_BG = (0, 0, 0, 180)  # 검정 반투명 — 텍스트 배경
COLOR_TEXT_FG = (255, 255, 255) # 흰색 — 텍스트


def load_font(size: int = 18):
    """시스템 폰트 자동 탐색 (Windows 환경 우선)"""
    candidates = [
        "C:/Windows/Fonts/malgun.ttf",     # 맑은 고딕 (한글)
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_box(draw: ImageDraw.ImageDraw, coords: tuple, label: str | None = None, font=None):
    x1, y1, x2, y2 = coords
    draw.rectangle([x1, y1, x2, y2], outline=COLOR_BOX, width=3)
    if label:
        draw_label(draw, x1, y1 - 24, label, font)


def draw_highlight(draw: ImageDraw.ImageDraw, coords: tuple, img: Image.Image):
    x1, y1, x2, y2 = coords
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([x1, y1, x2, y2], fill=COLOR_HIGHLIGHT)
    combined = Image.alpha_composite(img.convert("RGBA"), overlay)
    return combined.convert("RGB")


def draw_arrow(draw: ImageDraw.ImageDraw, coords: tuple, label: str | None = None, font=None):
    x1, y1, x2, y2 = coords
    draw.line([x1, y1, x2, y2], fill=COLOR_ARROW, width=3)

    # 화살표 머리 (끝점 기준)
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    head_len = 15
    for offset in [0.4, -0.4]:
        hx = x2 - head_len * math.cos(angle + offset)
        hy = y2 - head_len * math.sin(angle + offset)
        draw.line([x2, y2, int(hx), int(hy)], fill=COLOR_ARROW, width=3)

    if label:
        draw_label(draw, x2 + 5, y2 - 12, label, font)


def draw_label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font=None):
    bbox = draw.textbbox((x, y), text, font=font)
    padding = 4
    draw.rectangle(
        [bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding],
        fill=COLOR_TEXT_BG
    )
    draw.text((x, y), text, fill=COLOR_TEXT_FG, font=font)


def parse_coords(s: str) -> tuple:
    parts = s.split(",")
    if len(parts) != 4:
        raise ValueError(f"좌표는 x1,y1,x2,y2 형식이어야 합니다: '{s}'")
    return tuple(int(p) for p in parts)


def parse_point(s: str) -> tuple:
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError(f"좌표는 x,y 형식이어야 합니다: '{s}'")
    return tuple(int(p) for p in parts)


def main():
    parser = argparse.ArgumentParser(description="이미지 주석 스크립트")
    parser.add_argument("--input", required=True, help="원본 이미지 경로")
    parser.add_argument("--out", default=None, help="저장 경로 (미지정 시 원본명_annotated.png)")
    parser.add_argument("--box", default=None, help="빨간 박스 좌표: x1,y1,x2,y2")
    parser.add_argument("--highlight", default=None, help="노란 하이라이트 좌표: x1,y1,x2,y2")
    parser.add_argument("--arrow", default=None, help="파란 화살표 좌표: x1,y1,x2,y2")
    parser.add_argument("--text", default=None, help="텍스트 삽입 위치: x,y")
    parser.add_argument("--label", default=None, help="박스/화살표/텍스트에 붙일 설명")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] 파일 없음: {input_path}", file=sys.stderr)
        sys.exit(1)

    img = Image.open(input_path).convert("RGB")
    font = load_font(18)

    # 하이라이트는 레이어 합성이 필요하여 먼저 처리
    if args.highlight:
        coords = parse_coords(args.highlight)
        img = draw_highlight(None, coords, img)

    draw = ImageDraw.Draw(img)

    if args.box:
        draw_box(draw, parse_coords(args.box), args.label, font)

    if args.arrow:
        draw_arrow(draw, parse_coords(args.arrow), args.label if not args.box else None, font)

    if args.text:
        x, y = parse_point(args.text)
        if args.label:
            draw_label(draw, x, y, args.label, font)

    # 저장 경로 결정
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = input_path.parent / (input_path.stem + "_annotated.png")

    img.save(str(out_path))
    print(f"[OK] 주석 이미지 저장: {out_path}")


if __name__ == "__main__":
    main()
