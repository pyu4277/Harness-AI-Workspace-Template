"""
VideoAnalyzer Pipeline - Stage 1A: Extract (프레임 추출 + 자막 파싱)
흡수 출처: TransTest/pipeline/01_extract_frames.py 개량 (Reference-Port)

개량 v2: 다중 영상 지원, .ko.srt 자막 매칭, 영상별 서브디렉토리
"""
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np

from config_loader import load_config
from path_utils import get_path, ensure_dir

VIDEO_EXTENSIONS = (".mp4", ".avi", ".mkv", ".mov", ".webm")


def find_all_videos(video_dir: Path) -> list[Path]:
    """입력 디렉토리에서 모든 영상 파일을 찾는다."""
    videos = sorted(f for f in video_dir.iterdir() if f.suffix.lower() in VIDEO_EXTENSIONS)
    if not videos:
        print(f"오류: 영상 파일을 찾을 수 없습니다: {video_dir}")
        print(f"  지원 포맷: {', '.join(VIDEO_EXTENSIONS)}")
        sys.exit(1)
    return videos


def extract_frames(video_path: Path, output_dir: Path, interval: float) -> list[Path]:
    """영상에서 설정 간격으로 프레임을 추출한다."""
    ensure_dir(output_dir)

    # Windows 한국어 경로 호환: VideoCapture에 바이트 경로 사용 불가 시 대비
    video_str = str(video_path)
    cap = cv2.VideoCapture(video_str)
    if not cap.isOpened():
        # 한국어 경로 fallback: 짧은 경로명(8.3) 시도
        import ctypes
        buf = ctypes.create_unicode_buffer(300)
        ctypes.windll.kernel32.GetShortPathNameW(video_str, buf, 300)
        cap = cv2.VideoCapture(buf.value)
    if not cap.isOpened():
        print(f"오류: 영상 파일을 열 수 없습니다: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    frame_skip = int(fps * interval)

    print(f"  영상: {fps:.1f}fps, {total_frames}프레임, {duration:.1f}초 ({duration/60:.1f}분)")
    print(f"  추출 간격: {interval}초 ({frame_skip}프레임마다)")
    print(f"  예상 프레임 수: {int(duration / interval)}장")

    extracted_paths = []
    frame_idx = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_skip == 0:
            saved_count += 1
            filename = output_dir / f"frame_{saved_count:06d}.jpg"
            # Windows 한국어 경로 호환: imencode + 바이트 쓰기
            success, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            if success:
                filename.write_bytes(buf.tobytes())
            extracted_paths.append(filename)

            if saved_count % 1000 == 0:
                print(f"  {saved_count}장 추출 완료...")

        frame_idx += 1

    cap.release()
    print(f"  프레임 추출 완료: {saved_count}장 -> {output_dir}")
    return extracted_paths


def parse_srt(srt_path: Path) -> list[dict]:
    """SRT 자막 파일을 파싱한다. BOM 처리 포함."""
    with open(srt_path, encoding="utf-8-sig") as f:
        content = f.read()

    pattern = re.compile(
        r"(\d+)\s*\n"
        r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*\n"
        r"((?:(?!\n\n|\d+\s*\n\d{2}:\d{2}).+\n?)+)",
        re.MULTILINE,
    )

    segments = []
    for m in pattern.finditer(content):
        seg_id = int(m.group(1))
        start = int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4)) + int(m.group(5)) / 1000
        end = int(m.group(6)) * 3600 + int(m.group(7)) * 60 + int(m.group(8)) + int(m.group(9)) / 1000
        text = m.group(10).strip().replace("\n", " ")

        segments.append({
            "id": seg_id,
            "start": round(start, 3),
            "end": round(end, 3),
            "text": text,
        })

    return segments


def find_subtitle(video_path: Path) -> Path | None:
    """영상과 동일 디렉토리에서 매칭되는 자막 파일을 찾는다.
    검색 순서: stem.ko.srt -> stem.srt -> stem.txt"""
    stem = video_path.stem
    parent = video_path.parent
    for suffix in (".ko.srt", ".srt", ".txt"):
        candidate = parent / f"{stem}{suffix}"
        if candidate.exists():
            return candidate
    return None


def save_transcript(segments: list[dict], output_path: Path, source: str, language: str) -> None:
    """트랜스크립트를 JSON으로 저장한다."""
    data = {
        "source": source,
        "language": language,
        "segment_count": len(segments),
        "segments": segments,
    }
    ensure_dir(output_path.parent)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  트랜스크립트 저장: {len(segments)}개 세그먼트 -> {output_path}")


def process_single_video(video_path: Path, frames_base: Path, interval: float, language: str) -> None:
    """단일 영상의 프레임 추출 + 자막 파싱을 처리한다."""
    stem = video_path.stem
    frames_dir = frames_base / stem
    print(f"\n--- [{stem}] ---")

    # 이미 추출된 경우 건너뛰기
    existing = list(frames_dir.glob("frame_*.jpg")) if frames_dir.exists() else []
    if existing:
        print(f"  이미 {len(existing)}장 추출됨. 건너뜁니다. (재추출: 폴더 삭제 후 재실행)")
        return

    # 프레임 추출
    extract_frames(video_path, frames_dir, interval)

    # 자막 처리
    subtitle_path = find_subtitle(video_path)
    transcript_output = frames_dir / "transcript.json"

    if subtitle_path:
        print(f"  자막 발견: {subtitle_path.name}")
        segments = parse_srt(subtitle_path)
        save_transcript(segments, transcript_output, source="subtitle", language=language)
    else:
        print("  자막 없음 -> Whisper 필요 (02_whisper_transcribe.py)")
        save_transcript([], transcript_output, source="pending_whisper", language=language)


def main():
    """Stage 1A 메인: 모든 영상의 프레임 추출 + 자막 파싱."""
    config = load_config()
    interval = config["pipeline"]["frame_interval"]
    language = config["pipeline"]["whisper_language"]

    video_dir = get_path(config, "input_video")
    frames_base = get_path(config, "workspace_frames")

    videos = find_all_videos(video_dir)
    print(f"\n=== Stage 1A: Extract ===")
    print(f"영상 {len(videos)}개 발견:")
    for v in videos:
        size_mb = v.stat().st_size / (1024 * 1024)
        print(f"  - {v.name} ({size_mb:.0f}MB)")

    for video_path in videos:
        process_single_video(video_path, frames_base, interval, language)

    print(f"\n=== Stage 1A 전체 완료 ===")
    for v in videos:
        stem = v.stem
        fdir = frames_base / stem
        count = len(list(fdir.glob("frame_*.jpg"))) if fdir.exists() else 0
        print(f"  [{stem}] {count}장")


if __name__ == "__main__":
    main()
