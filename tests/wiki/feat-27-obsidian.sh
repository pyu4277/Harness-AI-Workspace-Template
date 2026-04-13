#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/obsidian-detect.js"
out=$(node "$SCRIPT" 2>/dev/null)
echo "$out" | grep -q '"preservation"' || { echo "FAIL feat-27 preservation keys"; echo "$out"; exit 1; }
echo "$out" | grep -q '"scanned"' || { echo "FAIL feat-27 scanned"; exit 1; }
echo "PASS feat-27 (obsidian-detect preservation scan)"
