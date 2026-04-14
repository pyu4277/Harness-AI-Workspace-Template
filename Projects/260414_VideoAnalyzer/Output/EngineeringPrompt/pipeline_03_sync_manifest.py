"""
VideoAnalyzer Pipeline - Stage 2B: 동기화 매니페스트 생성
장면 분할 결과 + 트랜스크립트를 매칭하여 manifest.json을 생성한다.
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
        # 자막 세그먼트가 장면 시간 범위와 겹치는지 확인
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


def main():
    """Stage 2B: 동기화 매니페스트 생성 메인."""
    config = load_config()

    frames_dir = get_path(config, "workspace_frames")
    manifest_dir = get_path(config, "workspace_manifest")
    ensure_dir(manifest_dir)

    print(f"\n=== Stage 2B: 동기화 매니페스트 생성 ===")

    # 장면 분할 결과 로드
    scenes_data = load_json(manifest_dir / "scenes.json")
    scenes = scenes_data["scenes"]

    # 트랜스크립트 로드
    transcript_path = frames_dir / "transcript.json"
    transcript_data = load_json(transcript_path)
    segments = transcript_data.get("segments", [])

    if not segments:
        print("경고: 트랜스크립트가 비어 있습니다. 시각 분석만 가능합니다.")

    # 장면-자막 매칭
    for scene in scenes:
        scene["transcript_text"] = match_transcript(scene, segments)
        scene["transcript_segments"] = match_segment_ids(scene, segments)

    # 영상 이름 추출 (video 디렉토리의 파일명)
    video_dir = get_path(config, "input_video")
    video_files = list(video_dir.glob("*.*"))
    video_name = video_files[0].stem if video_files else "unknown"

    # manifest.json 생성
    manifest = {
        "video_name": video_name,
        "total_frames": scenes_data["total_frames"],
        "total_duration": scenes_data["total_duration"],
        "total_scenes": len(scenes),
        "ssim_threshold": scenes_data["ssim_threshold"],
        "transcript_source": transcript_data.get("source", "unknown"),
        "transcript_language": transcript_data.get("language", "unknown"),
        "scenes": scenes,
    }

    manifest_path = manifest_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"매니페스트 생성 완료: {len(scenes)}개 장면 -> {manifest_path}")

    # 매칭 통계
    matched = sum(1 for s in scenes if s["transcript_text"])
    print(f"자막 매칭: {matched}/{len(scenes)} 장면 ({matched/len(scenes)*100:.0f}%)")

    for s in scenes:
        text_preview = s["transcript_text"][:50] + "..." if len(s["transcript_text"]) > 50 else s["transcript_text"]
        mins = int(s["start_time"] // 60)
        secs = int(s["start_time"] % 60)
        print(f"  [{s['scene_id']:3d}] {mins}:{secs:02d} | {text_preview or '(자막 없음)'}")


if __name__ == "__main__":
    main()
