#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/wiki-query.py"
for L in 0 100 800; do
  out=$(python "$SCRIPT" "AI" --layer "$L" --top-k 3 2>&1)
  echo "$out" | grep -q "\"layer\": $L" || { echo "FAIL feat-25 layer=$L"; exit 1; }
done
echo "PASS feat-25 (3-layer 0/100/800 budgets)"
