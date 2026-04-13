#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/daemon-5min.py"
out=$(python "$SCRIPT" --once 2>&1)
echo "$out" | grep -q "'ok':" || { echo "FAIL feat-30"; echo "$out"; exit 1; }
echo "PASS feat-30 (daemon-5min once tick)"
