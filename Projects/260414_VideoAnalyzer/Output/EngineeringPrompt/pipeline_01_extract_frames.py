"""
VideoAnalyzer Pipeline - Stage 1A: Extract (프레임 추출 + 자막 파싱)
흡수 출처: TransTest/pipeline/01_extract_frames.py 개량 (Reference-Port)

개량 사항:
- 하드코딩 경로 -> config.json 외부화
- 프레임 파일명 6자리 제로패딩 (frame_NNNNNN.jpg)
- .srt 파싱 지원 추가
- transcript.json에 source 메타데이터 포함
"""
import json
import re
import sys
from pathlib import Path

import cv2

from config_loader import load_config
from path_utils import get_path, ensure_dir


def find_video_file(video_dir: Path) -> Path:
    """입력 디렉토리에서 영상 파일을 찾는다."""
    extensions = (".mp4", ".avi", ".mkv", ".mov", ".webm")
    videos = [f for f in video_dir.iterdir() if f.suffix.lower() in extensions]
    if not videos:
        print(f"오류: 영상 파일을 찾을 수 없습니다: {video_dir}")
        print(f"  지원 포맷: {', '.join(extensions)}")
        sys.exit(1)
    if len(videos) > 1:
        print(f"경고: 영상 파일이 {len(videos)}개 발견됨. 첫 번째 사용: {videos[0].name}")
    return videos[0]


def extract_frames(video_path: Path, output_dir: Path, interval: float) -> list[Path]:
    """영상에서 설정 간격으로 프레임을 추출한다."""
    ensure_dir(output_dir)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"오류: 영상 파일을 열 수 없습니다: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    frame_skip = int(fps * interval)

    print(f"영상 정보: {fps:.1f}fps, {total_frames}프레임, {duration:.1f}초 ({duration/60:.1f}분)")
    print(f"추출 간격: {interval}초 ({frame_skip}프레임마다)")

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
            cv2.imwrite(str(filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            extracted_paths.append(filename)

        frame_idx += 1

    cap.release()
    print(f"프레임 추출 완료: {saved_count}장 -> {output_dir}")
    return extracted_paths


def parse_srt(srt_path: Path) -> list[dict]:
    """SRT 자막 파일을 파싱한다."""
    with open(srt_path, encoding="utf-8") as f:
        content = f.read()

    # SRT 형식: ID\nHH:MM:SS,mmm --> HH:MM:SS,mmm\ntext\n\n
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


def parse_txt_transcript(txt_path: Path) -> list[dict]:
    """타임스탬프가 포함된 텍스트 자막을 파싱한다. (분:초 형식)"""
    with open(txt_path, encoding="utf-8") as f:
        content = f.read()

    time_pattern = re.compile(r"^(\d+):(\d{2})$", re.MULTILINE)
    matches = list(time_pattern.finditer(content))

    segments = []
    for i, match in enumerate(matches):
        start_sec = int(match.group(1)) * 60 + int(match.group(2))

        text_start = match.end()
        text_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        text = content[text_start:text_end].strip()

        if not text or re.match(r"^\d+:\d{2}$", text):
            continue

        end_sec = (int(matches[i + 1].group(1)) * 60 + int(matches[i + 1].group(2))) if i + 1 < len(matches) else start_sec + 3

        segments.append({
            "id": len(segments) + 1,
            "start": float(start_sec),
            "end": float(end_sec),
            "text": text,
        })

    return segments


def find_subtitle(subtitle_dir: Path, video_name: str) -> Path | None:
    """영상명과 매칭되는 자막 파일을 찾는다."""
    stem = Path(video_name).stem
    for ext in (".srt", ".txt", ".md"):
        candidate = subtitle_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    # 이름 무관하게 파일이 하나뿐이면 사용
    subs = list(subtitle_dir.glob("*.srt")) + list(subtitle_dir.glob("*.txt"))
    if len(subs) == 1:
        return subs[0]
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
    print(f"트랜스크립트 저장 완료: {len(segments)}개 세그먼트 -> {output_path}")


def main():
    """Stage 1A 메인: 프레임 추출 + 자막 파싱."""
    config = load_config()
    interval = config["pipeline"]["frame_interval"]
    language = config["pipeline"]["whisper_language"]

    video_dir = get_path(config, "input_video")
    subtitle_dir = get_path(config, "input_subtitle")
    frames_dir = get_path(config, "workspace_frames")

    # 1. 영상 파일 찾기
    video_path = find_video_file(video_dir)
    print(f"\n=== Stage 1A: Extract ===")
    print(f"영상: {video_path.name}")

    # 2. 프레임 추출
    extract_frames(video_path, frames_dir, interval)

    # 3. 자막 처리
    subtitle_path = find_subtitle(subtitle_dir, video_path.name)
    transcript_output = frames_dir / "transcript.json"

    if subtitle_path:
        print(f"자막 발견: {subtitle_path.name}")
        if subtitle_path.suffix.lower() == ".srt":
            segments = parse_srt(subtitle_path)
        else:
            segments = parse_txt_transcript(subtitle_path)
        save_transcript(segments, transcript_output, source="subtitle", language=language)
    else:
        print("자막 파일 없음 -> Whisper 음성추출 필요 (02_whisper_transcribe.py 실행)")
        # Whisper 자동 호출은 02에서 처리
        save_transcript([], transcript_output, source="pending_whisper", language=language)

    print(f"\n동기화 정보:")
    frame_count = len(list(frames_dir.glob("frame_*.jpg")))
    print(f"  프레임 {frame_count}장 (간격 {interval}초)")
    if subtitle_path:
        print(f"  자막 세그먼트 {len(segments)}개")


if __name__ == "__main__":
    main()
