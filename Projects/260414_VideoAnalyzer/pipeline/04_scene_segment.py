"""
VideoAnalyzer Pipeline - Stage 2A: SSIM 기반 장면 분할
흡수 출처: TransTest/pipeline/02_scene_segment.py 개량 (Reference-Port)

개량 v2: 다중 영상 서브디렉토리 지원
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

from config_loader import load_config
from path_utils import get_path, ensure_dir


def load_frame_list(frames_dir: Path) -> list[Path]:
    """프레임 디렉토리에서 정렬된 프레임 목록을 반환한다."""
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    if not frames:
        print(f"오류: 프레임을 찾을 수 없습니다: {frames_dir}")
        sys.exit(1)
    return frames


def calculate_ssim_scores(frames: list[Path]) -> list[float]:
    """연속 프레임 쌍의 SSIM을 계산한다."""
    print(f"  SSIM 계산 중... ({len(frames)}장)")
    scores = [1.0]
    prev_gray = None

    for i, fpath in enumerate(frames):
        # Windows 한국어 경로 호환: imdecode 사용
        img = cv2.imdecode(np.fromfile(str(fpath), dtype=np.uint8), cv2.IMREAD_COLOR)
        small = cv2.resize(img, (480, 270))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            score = ssim(prev_gray, gray)
            scores.append(score)

        prev_gray = gray

        if (i + 1) % 500 == 0:
            print(f"    {i + 1}/{len(frames)} 완료")

    print(f"  SSIM 완료 (평균: {np.mean(scores):.3f}, 최소: {np.min(scores):.3f})")
    return scores


def detect_boundaries(ssim_scores: list[float], threshold: float, min_frames: int) -> list[int]:
    """SSIM 점수에서 장면 경계를 탐지한다."""
    boundaries = [0]
    for i, score in enumerate(ssim_scores):
        if score < threshold and i - boundaries[-1] >= min_frames:
            boundaries.append(i)
    total = len(ssim_scores)
    if total - 1 not in boundaries:
        boundaries.append(total - 1)
    return boundaries


def build_scenes(boundaries: list[int], frames: list[Path], interval: float) -> list[dict]:
    """경계 목록에서 장면 정보를 구성한다."""
    scenes = []
    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i + 1]
        start_time = start * interval
        end_time = end * interval
        mid = (start + end) // 2
        representative = frames[mid].name

        scenes.append({
            "scene_id": i + 1,
            "start_frame": start + 1,
            "end_frame": end + 1,
            "start_time": round(start_time, 1),
            "end_time": round(end_time, 1),
            "duration": round(end_time - start_time, 1),
            "representative_frame": representative,
            "frame_count": end - start,
        })
    return scenes


def process_single_video(video_stem: str, frames_base: Path, manifest_base: Path,
                          threshold: float, min_duration: float, interval: float) -> None:
    """단일 영상의 장면 분할을 처리한다."""
    frames_dir = frames_base / video_stem
    manifest_dir = manifest_base / video_stem
    ensure_dir(manifest_dir)

    scenes_path = manifest_dir / "scenes.json"
    if scenes_path.exists():
        print(f"  이미 분할 완료. 건너뜁니다.")
        return

    if not frames_dir.exists():
        print(f"  프레임 디렉토리 없음: {frames_dir}")
        return

    frames = load_frame_list(frames_dir)
    print(f"  프레임 {len(frames)}장 로드")

    ssim_scores = calculate_ssim_scores(frames)

    min_frames = int(min_duration / interval)
    boundaries = detect_boundaries(ssim_scores, threshold, min_frames)
    scenes = build_scenes(boundaries, frames, interval)

    with open(scenes_path, "w", encoding="utf-8") as f:
        json.dump({
            "video_stem": video_stem,
            "total_frames": len(frames),
            "total_duration": round(len(frames) * interval, 1),
            "ssim_threshold": threshold,
            "scene_count": len(scenes),
            "scenes": scenes,
        }, f, ensure_ascii=False, indent=2)

    reduction = 1 - (len(scenes) / len(frames))
    print(f"  장면 분할 완료: {len(scenes)}개 장면 (중복 제거 {reduction:.1%})")


def main():
    """Stage 2A: 모든 영상의 SSIM 장면 분할."""
    config = load_config()
    threshold = config["pipeline"]["ssim_threshold"]
    min_duration = config["pipeline"]["min_scene_duration"]
    interval = config["pipeline"]["frame_interval"]

    frames_base = get_path(config, "workspace_frames")
    manifest_base = get_path(config, "workspace_manifest")

    # 프레임이 존재하는 영상 서브디렉토리 탐색
    video_dirs = sorted(d for d in frames_base.iterdir() if d.is_dir() and list(d.glob("frame_*.jpg")))
    if not video_dirs:
        print("오류: 추출된 프레임이 없습니다. Stage 1을 먼저 실행하세요.")
        sys.exit(1)

    print(f"\n=== Stage 2A: SSIM 장면 분할 ===")
    print(f"임계값: {threshold}, 최소 장면 길이: {min_duration}초")
    print(f"영상 {len(video_dirs)}개 처리:")

    for vdir in video_dirs:
        stem = vdir.name
        print(f"\n--- [{stem}] ---")
        process_single_video(stem, frames_base, manifest_base, threshold, min_duration, interval)

    print(f"\n=== Stage 2A 전체 완료 ===")


if __name__ == "__main__":
    main()
