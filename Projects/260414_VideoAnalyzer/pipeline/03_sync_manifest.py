"""
VideoAnalyzer Pipeline - Stage 2B: 동기화 매니페스트 생성
장면 분할 결과 + 트랜스크립트를 매칭하여 manifest.json을 생성한다.

개량 v2: 다중 영상 서브디렉토리 지원
"""
import json
import sys
from pathlib import Path

from config_loader import load_config
from path_utils import get_path, ensure_dir


def load_json(path: Path) -> dict:
    """JSON 파일을 로드한다."""
    if not path.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def match_transcript(scene: dict, segments: list[dict]) -> str:
    """장면의 시간 범위에 해당하는 자막 텍스트를 매칭한다."""
    matched = []
    for seg in segments:
        if seg["end"] > scene["start_time"] and seg["start"] < scene["end_time"]:
            matched.append(seg["text"])
    return " ".join(matched)


def match_segment_ids(scene: dict, segments: list[dict]) -> list[int]:
    """장면에 매칭되는 자막 세그먼트 ID 목록을 반환한다."""
    ids = []
    for seg in segments:
        if seg["end"] > scene["start_time"] and seg["start"] < scene["end_time"]:
            ids.append(seg["id"])
    return ids


def process_single_video(video_stem: str, frames_base: Path, manifest_base: Path) -> None:
    """단일 영상의 매니페스트를 생성한다."""
    manifest_dir = manifest_base / video_stem
    frames_dir = frames_base / video_stem

    manifest_path = manifest_dir / "manifest.json"
    if manifest_path.exists():
        print(f"  이미 매니페스트 존재. 건너뜁니다.")
        return

    # 장면 분할 결과 로드
    scenes_path = manifest_dir / "scenes.json"
    if not scenes_path.exists():
        print(f"  scenes.json 없음. Stage 2A를 먼저 실행하세요.")
        return

    scenes_data = load_json(scenes_path)
    scenes = scenes_data["scenes"]

    # 트랜스크립트 로드
    transcript_path = frames_dir / "transcript.json"
    if transcript_path.exists():
        transcript_data = load_json(transcript_path)
        segments = transcript_data.get("segments", [])
    else:
        print(f"  transcript.json 없음. 시각 분석만 가능합니다.")
        transcript_data = {"source": "none", "language": "unknown"}
        segments = []

    if not segments:
        print("  경고: 트랜스크립트가 비어 있습니다.")

    # 장면-자막 매칭
    for scene in scenes:
        scene["transcript_text"] = match_transcript(scene, segments)
        scene["transcript_segments"] = match_segment_ids(scene, segments)

    # manifest.json 생성
    manifest = {
        "video_name": video_stem,
        "total_frames": scenes_data["total_frames"],
        "total_duration": scenes_data["total_duration"],
        "total_scenes": len(scenes),
        "ssim_threshold": scenes_data["ssim_threshold"],
        "transcript_source": transcript_data.get("source", "unknown"),
        "transcript_language": transcript_data.get("language", "unknown"),
        "scenes": scenes,
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    matched = sum(1 for s in scenes if s["transcript_text"])
    print(f"  매니페스트 생성: {len(scenes)}개 장면, 자막 매칭 {matched}/{len(scenes)}")

    for s in scenes:
        text_preview = s["transcript_text"][:50] + "..." if len(s["transcript_text"]) > 50 else s["transcript_text"]
        mins = int(s["start_time"] // 60)
        secs = int(s["start_time"] % 60)
        print(f"    [{s['scene_id']:3d}] {mins}:{secs:02d} | {text_preview or '(자막 없음)'}")


def main():
    """Stage 2B: 모든 영상의 동기화 매니페스트 생성."""
    config = load_config()

    frames_base = get_path(config, "workspace_frames")
    manifest_base = get_path(config, "workspace_manifest")

    # scenes.json이 존재하는 영상 서브디렉토리 탐색
    video_dirs = sorted(
        d for d in manifest_base.iterdir()
        if d.is_dir() and (d / "scenes.json").exists()
    )
    if not video_dirs:
        print("오류: 장면 분할 결과가 없습니다. Stage 2A를 먼저 실행하세요.")
        sys.exit(1)

    print(f"\n=== Stage 2B: 동기화 매니페스트 생성 ===")
    print(f"영상 {len(video_dirs)}개 처리:")

    for vdir in video_dirs:
        stem = vdir.name
        print(f"\n--- [{stem}] ---")
        process_single_video(stem, frames_base, manifest_base)

    print(f"\n=== Stage 2B 전체 완료 ===")


if __name__ == "__main__":
    main()
