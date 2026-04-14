"""
VideoAnalyzer Pipeline - Stage 3C-1.5: OpenCV 시각 사전 분류 (Pass 1.5)
Edge density + 얼굴 탐지로 프레임을 자동 분류한다.
LLM 없이 빠르게 토킹 헤드/빈 화면/콘텐츠 슬라이드를 구분한다.

분류 카테고리:
  CONTENT_RICH: 엣지 밀도 높음 (코드, 표, 다이어그램 가능성)
  TALKING_HEAD: 얼굴 탐지 + 엣지 밀도 낮음
  SPARSE_SCREEN: 엣지 밀도 매우 낮음 (빈 화면, 로고, 전환)
  MIXED: 얼굴 + 콘텐츠 혼합 (화면 공유 + 웹캠 등)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

from config_loader import load_config
from path_utils import get_path


# 임계값 (config에서 관리 가능하도록 상수 분리)
EDGE_HIGH_THRESHOLD = 0.08     # 엣지 비율 이상이면 콘텐츠 풍부
EDGE_LOW_THRESHOLD = 0.02      # 엣지 비율 이하이면 빈 화면
FACE_MIN_SIZE = (60, 60)       # 최소 얼굴 크기 (픽셀)
FACE_AREA_RATIO = 0.05         # 얼굴 영역이 화면의 N% 이상이면 토킹 헤드 후보


def load_frame(frame_path: Path) -> np.ndarray | None:
    """한국어 경로 호환 프레임 로드."""
    data = np.fromfile(str(frame_path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img


def calc_edge_density(img: np.ndarray) -> float:
    """Canny 엣지 밀도를 계산한다 (0~1)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (480, 270))
    edges = cv2.Canny(small, 50, 150)
    return np.count_nonzero(edges) / edges.size


def detect_faces(img: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Haar cascade로 얼굴을 탐지한다."""
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    cascade = cv2.CascadeClassifier(cascade_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (480, 270))
    faces = cascade.detectMultiScale(small, scaleFactor=1.1, minNeighbors=5,
                                     minSize=FACE_MIN_SIZE)
    if len(faces) == 0:
        return []
    return [(x, y, w, h) for x, y, w, h in faces]


def calc_face_area_ratio(faces: list, img_area: int) -> float:
    """전체 이미지 대비 얼굴 영역 비율."""
    if not faces:
        return 0.0
    total_face_area = sum(w * h for _, _, w, h in faces)
    # 480x270으로 리사이즈한 이미지 기준
    return total_face_area / (480 * 270)


def classify_frame(edge_density: float, faces: list, face_ratio: float) -> str:
    """프레임을 시각적으로 분류한다."""
    has_face = len(faces) > 0 and face_ratio >= FACE_AREA_RATIO

    if edge_density >= EDGE_HIGH_THRESHOLD:
        if has_face:
            return "MIXED"           # 얼굴 + 콘텐츠 (화면 공유 + 웹캠)
        return "CONTENT_RICH"        # 코드, 표, 다이어그램
    elif edge_density <= EDGE_LOW_THRESHOLD:
        return "SPARSE_SCREEN"       # 빈 화면, 로고
    elif has_face:
        return "TALKING_HEAD"        # 얼굴 위주
    else:
        return "CONTENT_RICH"        # 중간 밀도지만 얼굴 없음 → 콘텐츠 가능성


def process_single_video(video_stem: str, analysis_base: Path, frames_base: Path) -> None:
    """단일 영상의 모든 대표 프레임에 시각 사전 분류를 수행한다."""
    analysis_dir = analysis_base / video_stem
    frames_dir = frames_base / video_stem
    vprefilter_path = analysis_dir / "visual_prefilter.json"

    if vprefilter_path.exists():
        print(f"  이미 시각 분류 완료. 건너뜁니다.")
        return

    # 장면 파일에서 대표 프레임 목록 추출
    scene_files = sorted(analysis_dir.glob("scene_*.json"))
    if not scene_files:
        print(f"  장면 파일 없음.")
        return

    results = []
    stats = {"CONTENT_RICH": 0, "TALKING_HEAD": 0, "SPARSE_SCREEN": 0, "MIXED": 0, "ERROR": 0}

    for i, sf in enumerate(scene_files):
        with open(sf, encoding="utf-8") as f:
            scene = json.load(f)

        frame_name = scene.get("frame_name", "")
        frame_path = frames_dir / frame_name

        if not frame_path.exists():
            results.append({
                "scene_id": scene["scene_id"],
                "frame_name": frame_name,
                "visual_class": "ERROR",
                "edge_density": 0,
                "face_count": 0,
                "face_area_ratio": 0,
            })
            stats["ERROR"] += 1
            continue

        img = load_frame(frame_path)
        if img is None:
            stats["ERROR"] += 1
            continue

        edge_density = calc_edge_density(img)
        faces = detect_faces(img)
        face_ratio = calc_face_area_ratio(faces, img.shape[0] * img.shape[1])
        visual_class = classify_frame(edge_density, faces, face_ratio)

        results.append({
            "scene_id": scene["scene_id"],
            "frame_name": frame_name,
            "visual_class": visual_class,
            "edge_density": round(edge_density, 4),
            "face_count": len(faces),
            "face_area_ratio": round(face_ratio, 4),
        })
        stats[visual_class] += 1

        if (i + 1) % 100 == 0:
            print(f"    {i + 1}/{len(scene_files)} 분류 완료...")

    # 결과 저장
    output = {
        "video_stem": video_stem,
        "total_scenes": len(results),
        "stats": stats,
        "thresholds": {
            "edge_high": EDGE_HIGH_THRESHOLD,
            "edge_low": EDGE_LOW_THRESHOLD,
            "face_area_ratio": FACE_AREA_RATIO,
        },
        "scenes": results,
    }

    with open(vprefilter_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  시각 분류 완료: {len(results)}개 장면")
    for cls, cnt in stats.items():
        if cnt > 0:
            print(f"    {cls}: {cnt}개")


def main():
    """Stage 3C-1.5: 모든 영상의 시각 사전 분류."""
    config = load_config()
    analysis_base = get_path(config, "workspace_analysis")
    frames_base = get_path(config, "workspace_frames")

    video_dirs = sorted(
        d for d in analysis_base.iterdir()
        if d.is_dir() and list(d.glob("scene_*.json"))
    )
    if not video_dirs:
        print("오류: 장면 분석 파일이 없습니다.")
        sys.exit(1)

    print(f"\n=== Stage 3C-1.5: OpenCV 시각 사전 분류 ===")
    print(f"영상 {len(video_dirs)}개 처리:")

    for vdir in video_dirs:
        stem = vdir.name
        print(f"\n--- [{stem}] ---")
        process_single_video(stem, analysis_base, frames_base)

    print(f"\n=== Stage 3C-1.5 전체 완료 ===")


if __name__ == "__main__":
    main()
