"""
VideoAnalyzer Pipeline -- 경로 유틸리티
프로젝트 루트 기준 상대경로를 관리한다. 절대경로 하드코딩 금지.
"""
from pathlib import Path


def get_project_root() -> Path:
    """pipeline/ 상위 디렉토리를 프로젝트 루트로 반환한다."""
    return Path(__file__).parent.parent


def get_path(config: dict, key: str) -> Path:
    """config의 paths 섹션에서 키에 해당하는 절대경로를 반환한다."""
    relative = config["paths"][key]
    return get_project_root() / relative


def ensure_dir(path: Path) -> Path:
    """디렉토리가 없으면 생성하고 경로를 반환한다."""
    path.mkdir(parents=True, exist_ok=True)
    return path
