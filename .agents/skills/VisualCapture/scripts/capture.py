"""
capture.py — 화면 캡처 스크립트

사용법:
  # 전체 화면 캡처
  python capture.py --out "Projects/YYMMDD_이름/Input/captures/"

  # 특정 영역만 캡처 (left top width height)
  python capture.py --region 0 0 1280 720 --out "Projects/YYMMDD_이름/Input/captures/"

  # 특정 창 이름으로 캡처 (Windows)
  python capture.py --window "한글" --out "Projects/YYMMDD_이름/Input/captures/"

  # 파일명 직접 지정
  python capture.py --out "Projects/YYMMDD_이름/Input/captures/" --name "에러_로그인실패"

의존성: pip install pyautogui Pillow pygetwindow
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

try:
    import pyautogui
    from PIL import Image
except ImportError:
    print("[ERROR] 필수 패키지 없음. 설치: pip install pyautogui Pillow", file=sys.stderr)
    sys.exit(1)


def capture_fullscreen(output_path: Path) -> Path:
    screenshot = pyautogui.screenshot()
    screenshot.save(str(output_path))
    return output_path


def capture_region(left: int, top: int, width: int, height: int, output_path: Path) -> Path:
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot.save(str(output_path))
    return output_path


def capture_window(window_title: str, output_path: Path) -> Path:
    try:
        import pygetwindow as gw
    except ImportError:
        print("[ERROR] pygetwindow 없음. 설치: pip install pygetwindow", file=sys.stderr)
        sys.exit(1)

    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"[ERROR] '{window_title}' 창을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    win = windows[0]
    win.activate()
    import time
    time.sleep(0.3)  # 창 활성화 대기

    region = (win.left, win.top, win.width, win.height)
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save(str(output_path))
    return output_path


def make_filename(name: str | None) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = f"_{name}" if name else ""
    return f"capture_{ts}{label}.png"


def main():
    parser = argparse.ArgumentParser(description="화면 캡처 스크립트")
    parser.add_argument("--out", required=True, help="저장 폴더 경로 (상대경로 가능)")
    parser.add_argument("--name", default=None, help="파일명 설명 태그 (선택)")
    parser.add_argument("--region", nargs=4, type=int, metavar=("LEFT", "TOP", "WIDTH", "HEIGHT"),
                        help="캡처 영역 지정")
    parser.add_argument("--window", default=None, help="특정 창 이름으로 캡처")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / make_filename(args.name)

    if args.window:
        result = capture_window(args.window, output_path)
    elif args.region:
        left, top, width, height = args.region
        result = capture_region(left, top, width, height, output_path)
    else:
        result = capture_fullscreen(output_path)

    print(f"[OK] 캡처 저장: {result}")


if __name__ == "__main__":
    main()
