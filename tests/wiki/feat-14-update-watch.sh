#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/watch-daemon.py"
out=$(python "$SCRIPT" --once 2>&1)
echo "$out" | grep -q "once-mode exit" || { echo "FAIL feat-14"; echo "$out"; exit 1; }
echo "PASS feat-14 (watch-daemon smoke)"
