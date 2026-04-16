"""
VideoAnalyzer Pipeline - Stage 2A: SSIM 기반 장면 분할
흡수 출처: TransTest/pipeline/02_scene_segment.py 개량 (Reference-Port)

개량 사항:
- 하드코딩 경로/임계값 -> config.json 외부화
- 프레임 파일명 패턴 frame_NNNNNN.jpg 대응
- 대표 프레임 선택 로직 분리
- SSIM 리사이즈 크기 고정 (속도 향상)
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
    print(f"SSIM 계산 중... ({len(frames)}장)")
    scores = [1.0]  # 첫 프레임
    prev_gray = None

    for i, fpath in enumerate(frames):
        img = cv2.imread(str(fpath))
        small = cv2.resize(img, (480, 270))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            score = ssim(prev_gray, gray)
            scores.append(score)

        prev_gray = gray

        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(frames)} 완료")

    print(f"SSIM 계산 완료 (평균: {np.mean(scores):.3f}, 최소: {np.min(scores):.3f})")
    return scores


def detect_boundaries(ssim_scores: list[float], threshold: float, min_frames: int) -> list[int]:
    """SSIM 점수에서 장면 경계를 탐지한다."""
    boundaries = [0]

    for i, score in enumerate(ssim_scores):
        if score < threshold:
            if i - boundaries[-1] >= min_frames:
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


def main():
    """Stage 2A: SSIM 장면 분할 메인."""
    config = load_config()
    threshold = config["pipeline"]["ssim_threshold"]
    min_duration = config["pipeline"]["min_scene_duration"]
    interval = config["pipeline"]["frame_interval"]

    frames_dir = get_path(config, "workspace_frames")
    manifest_dir = get_path(config, "workspace_manifest")
    ensure_dir(manifest_dir)

    print(f"\n=== Stage 2A: SSIM 장면 분할 ===")
    print(f"임계값: {threshold}, 최소 장면 길이: {min_duration}초")

    # 프레임 로드
    frames = load_frame_list(frames_dir)
    print(f"프레임 {len(frames)}장 로드")

    # SSIM 계산
    ssim_scores = calculate_ssim_scores(frames)

    # 장면 경계 탐지
    min_frames = int(min_duration / interval)
    boundaries = detect_boundaries(ssim_scores, threshold, min_frames)
    scenes = build_scenes(boundaries, frames, interval)

    # 중간 저장 (03_sync_manifest에서 사용)
    scenes_path = manifest_dir / "scenes.json"
    with open(scenes_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_frames": len(frames),
            "total_duration": round(len(frames) * interval, 1),
            "ssim_threshold": threshold,
            "scene_count": len(scenes),
            "scenes": scenes,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n장면 분할 완료: {len(scenes)}개 장면 -> {scenes_path}")
    reduction = 1 - (len(scenes) / len(frames))
    print(f"중복 제거율: {reduction:.1%}")

    for s in scenes:
        mins = int(s["start_time"] // 60)
        secs = int(s["start_time"] % 60)
        print(f"  [{s['scene_id']:3d}] {mins}:{secs:02d} ~ {s['duration']:5.1f}초 | {s['representative_frame']}")


if __name__ == "__main__":
    main()
