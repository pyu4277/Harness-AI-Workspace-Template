#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/extract/audio-transcribe.py"
# whisper 미설치 시 graceful skip (exit 0)
F=$(mktemp --suffix=.wav)
trap 'rm -f "$F"' EXIT
echo "dummy" > "$F"
python "$SCRIPT" "$F" >/dev/null 2>&1 || { echo "FAIL feat-10 non-zero exit"; exit 1; }
echo "PASS feat-10 (audio-transcribe graceful)"
