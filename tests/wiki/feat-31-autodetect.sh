#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/llm-autodetect.py"
# 환경 변수 제거한 상태로 실행 → Ollama 없으면 ast-only 예상
out=$(env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY python "$SCRIPT" 2>&1)
echo "$out" | grep -q '"provider"' || { echo "FAIL feat-31"; echo "$out"; exit 1; }
echo "PASS feat-31 (llm-autodetect)"
