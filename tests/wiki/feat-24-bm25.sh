#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/wiki-query.py"
out=$(python "$SCRIPT" "wiki" --layer 0 --top-k 5 2>&1)
echo "$out" | grep -q '"layer": 0' || { echo "FAIL feat-24 layer"; echo "$out"; exit 1; }
echo "$out" | grep -q '"results"' || { echo "FAIL feat-24 results"; exit 1; }
echo "PASS feat-24 (BM25 layer-0)"
