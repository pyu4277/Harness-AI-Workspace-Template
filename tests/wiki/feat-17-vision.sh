#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/extract/vision-caption.py"
F=$(mktemp --suffix=.png)
trap 'rm -f "$F"' EXIT
printf '\x89PNG\r\n\x1a\n' > "$F"
out=$(python "$SCRIPT" "$F")
echo "$out" | grep -q '"delegation"' || { echo "FAIL feat-17"; exit 1; }
echo "$out" | grep -q "semantic-extractor" || { echo "FAIL feat-17 subagent ref"; exit 1; }
echo "PASS feat-17 (vision-caption delegation)"
