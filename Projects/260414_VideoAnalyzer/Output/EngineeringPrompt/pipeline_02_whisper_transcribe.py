"""
VideoAnalyzer Pipeline - Stage 1B: Whisper 음성추출
자막이 없을 때 Whisper로 자동 트랜스크립트를 생성한다.

의존성: pip install openai-whisper (사용자 승인 필수)
"""
import json
import subprocess
import sys
from pathlib import Path

from config_loader import load_config
from path_utils import get_path, ensure_dir


def extract_audio(video_path: Path, output_path: Path) -> Path:
    """ffmpeg로 영상에서 오디오를 추출한다."""
    ensure_dir(output_path.parent)
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        str(output_path), "-y",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        print(f"오류: ffmpeg 오디오 추출 실패")
        print(result.stderr[:500])
        sys.exit(1)
    print(f"오디오 추출 완료: {output_path}")
    return output_path


def transcribe(audio_path: Path, model_name: str, language: str) -> list[dict]:
    """Whisper로 음성을 트랜스크립트한다."""
    try:
        import whisper
    except ImportError:
        print("오류: openai-whisper가 설치되지 않았습니다.")
        print("  설치: pip install openai-whisper")
        sys.exit(1)

    print(f"Whisper 모델 로드 중: {model_name}")
    try:
        model = whisper.load_model(model_name)
    except Exception:
        # 메모리 부족 시 tiny 모델로 폴백
        print(f"경고: {model_name} 모델 로드 실패. tiny 모델로 폴백합니다.")
        model = whisper.load_model("tiny")

    print(f"음성 인식 중... (언어: {language})")
    result = model.transcribe(str(audio_path), language=language)

    segments = []
    for seg in result["segments"]:
        segments.append({
            "id": seg["id"] + 1,
            "start": round(seg["start"], 3),
            "end": round(seg["end"], 3),
            "text": seg["text"].strip(),
        })

    return segments


def main():
    """Stage 1B: Whisper 음성추출 메인."""
    config = load_config()
    model_name = config["pipeline"]["whisper_model"]
    language = config["pipeline"]["whisper_language"]

    video_dir = get_path(config, "input_video")
    audio_dir = get_path(config, "input_audio")
    frames_dir = get_path(config, "workspace_frames")

    # 기존 transcript.json 확인
    transcript_path = frames_dir / "transcript.json"
    if transcript_path.exists():
        with open(transcript_path, encoding="utf-8") as f:
            existing = json.load(f)
        if existing.get("source") != "pending_whisper":
            print("자막이 이미 존재합니다. Whisper 추출이 불필요합니다.")
            return

    # 영상 파일 찾기
    extensions = (".mp4", ".avi", ".mkv", ".mov", ".webm")
    videos = [f for f in video_dir.iterdir() if f.suffix.lower() in extensions]
    if not videos:
        print(f"오류: 영상 파일을 찾을 수 없습니다: {video_dir}")
        sys.exit(1)
    video_path = videos[0]

    print(f"\n=== Stage 1B: Whisper 음성추출 ===")
    print(f"영상: {video_path.name}")

    # 오디오 추출
    audio_path = audio_dir / f"{video_path.stem}.wav"
    extract_audio(video_path, audio_path)

    # Whisper 트랜스크립트
    segments = transcribe(audio_path, model_name, language)

    # 저장
    data = {
        "source": "whisper",
        "language": language,
        "model": model_name,
        "segment_count": len(segments),
        "segments": segments,
    }
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Whisper 트랜스크립트 완료: {len(segments)}개 세그먼트 -> {transcript_path}")


if __name__ == "__main__":
    main()
