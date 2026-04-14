"""
VideoAnalyzer Pipeline -- 공통 설정 로더
config.json을 로드하고 값 범위를 검증한다.
"""
import json
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

# 검증 범위 정의
_VALIDATION_RULES = {
    "pipeline.frame_interval": (0.1, 5.0),
    "pipeline.ssim_threshold": (0.5, 0.95),
    "pipeline.min_scene_duration": (1.0, 10.0),
    "report.image_max_width": (320, 3840),
    "report.image_quality": (10, 100),
    "report.max_report_size_mb": (1, 200),
}


def load_config(config_path: Path = None) -> dict:
    """config.json을 로드하고 검증한다."""
    path = config_path or CONFIG_PATH
    if not path.exists():
        print(f"오류: 설정 파일을 찾을 수 없습니다: {path}")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        config = json.load(f)

    validate_config(config)
    return config


def validate_config(config: dict) -> None:
    """설정값의 범위를 검증한다. 범위 초과 시 오류를 출력하고 종료한다."""
    for dotkey, (vmin, vmax) in _VALIDATION_RULES.items():
        section, key = dotkey.split(".")
        value = config.get(section, {}).get(key)
        if value is None:
            continue
        if not (vmin <= value <= vmax):
            print(f"오류: {dotkey} 값 {value}이(가) 범위를 벗어났습니다 ({vmin}~{vmax})")
            sys.exit(1)
