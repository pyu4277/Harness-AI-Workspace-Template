"""
VideoAnalyzer Pipeline - Stage 3A: 시각 분석 가이드
Claude Code 런타임에서 실행되는 분석 안내 스크립트.
실제 시각 분석은 Claude Read 도구로 수행된다 (이 스크립트는 분석 대상 목록 생성).

개량 v2: 다중 영상 서브디렉토리 지원
"""
import json
import sys
from pathlib import Path

from config_loader import load_config
from path_utils import get_path, ensure_dir


def process_single_video(video_stem: str, manifest_base: Path,
                          frames_base: Path, analysis_base: Path) -> None:
    """단일 영상의 시각 분석 대상 목록을 생성한다."""
    manifest_dir = manifest_base / video_stem
    frames_dir = frames_base / video_stem
    analysis_dir = analysis_base / video_stem
    ensure_dir(analysis_dir)

    manifest_path = manifest_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"  manifest.json 없음. Stage 2B를 먼저 실행하세요.")
        return

    targets_path = analysis_dir / "analysis_targets.json"
    if targets_path.exists():
        print(f"  이미 분석 대상 목록 존재. 건너뜁니다.")
        return

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    scenes = manifest["scenes"]
    print(f"  총 {len(scenes)}개 장면의 대표 프레임 분석 필요")

    analysis_targets = []
    for scene in scenes:
        frame_path = frames_dir / scene["representative_frame"]
        target = {
            "scene_id": scene["scene_id"],
            "frame_path": str(frame_path),
            "frame_name": scene["representative_frame"],
            "start_time": scene["start_time"],
            "end_time": scene["end_time"],
            "transcript_text": scene.get("transcript_text", ""),
            "analyzed": False,
        }
        analysis_targets.append(target)

        mins = int(scene["start_time"] // 60)
        secs = int(scene["start_time"] % 60)
        print(f"    [{scene['scene_id']:3d}] {mins}:{secs:02d} | {scene['representative_frame']}")

    with open(targets_path, "w", encoding="utf-8") as f:
        json.dump(analysis_targets, f, ensure_ascii=False, indent=2)

    print(f"  분석 대상 목록 저장: {targets_path}")


def main():
    """Stage 3A: 모든 영상의 시각 분석 대상 목록 생성."""
    config = load_config()

    manifest_base = get_path(config, "workspace_manifest")
    frames_base = get_path(config, "workspace_frames")
    analysis_base = get_path(config, "workspace_analysis")

    # manifest.json이 존재하는 영상 서브디렉토리 탐색
    video_dirs = sorted(
        d for d in manifest_base.iterdir()
        if d.is_dir() and (d / "manifest.json").exists()
    )
    if not video_dirs:
        print("오류: manifest.json이 없습니다. Stage 2를 먼저 실행하세요.")
        sys.exit(1)

    print(f"\n=== Stage 3A: 시각 분석 대상 ===")
    print(f"영상 {len(video_dirs)}개 처리:")

    for vdir in video_dirs:
        stem = vdir.name
        print(f"\n--- [{stem}] ---")
        process_single_video(stem, manifest_base, frames_base, analysis_base)

    print(f"\n=== Stage 3A 전체 완료 ===")
    print()
    print("=" * 60)
    print("다음 단계: Claude Code에서 각 프레임을 Read 도구로 분석하세요.")
    print("  - 각 대표 프레임 이미지를 Read로 열기")
    print("  - 시각 정보 추출 (도표, 수식, 코드, 회로도 등)")
    print("  - 자막에 없는 시각 전용 정보 식별")
    print("  - 분석 결과를 workspace/analysis/{stem}/scene_NNN.json으로 저장")
    print("=" * 60)


if __name__ == "__main__":
    main()
