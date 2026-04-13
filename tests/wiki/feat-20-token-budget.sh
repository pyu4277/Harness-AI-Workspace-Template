#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/token-budget.js"
out=$(printf "hello world" | node "$SCRIPT")
echo "$out" | grep -q '"approx_tokens"' || { echo "FAIL feat-20 keys"; exit 1; }
echo "$out" | grep -q '"fits_layer"' || { echo "FAIL feat-20 fits"; exit 1; }
echo "PASS feat-20 (token-budget.js)"
