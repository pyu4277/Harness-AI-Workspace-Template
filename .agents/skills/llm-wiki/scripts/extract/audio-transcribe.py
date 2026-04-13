#!/usr/bin/env python3
"""
audio-transcribe.py -- 오디오 파일 전사 (whisper CLI wrapper)
Reference-Port 출처: Graphify "Whisper pass" 아이디어만 차용

규칙: whisper 미설치 시 exit 0 + stderr 메시지 (graceful skip).
"""
import sys
import json
import shutil
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audio-transcribe.py <audio>"}))
        sys.exit(1)

    whisper = shutil.which("whisper")
    if not whisper:
        print(json.dumps({
            "skipped": True,
            "reason": "whisper CLI not installed",
            "install_hint": "pip install openai-whisper + ffmpeg",
        }), file=sys.stderr)
        sys.exit(0)

    audio = Path(sys.argv[1])
    if not audio.exists():
        print(json.dumps({"error": "file not found"}))
        sys.exit(1)

    try:
        result = subprocess.run(
            [whisper, str(audio), "--output_format", "txt", "--language", "ko"],
            capture_output=True, text=True, errors="replace", timeout=600,
        )
        print(json.dumps({
            "file": str(audio),
            "stdout_excerpt": result.stdout[:500],
            "returncode": result.returncode,
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
