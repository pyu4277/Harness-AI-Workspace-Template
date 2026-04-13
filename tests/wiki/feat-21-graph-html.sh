#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
# graph.json 이 없으면 feat-13 이 먼저 생성해야 함 — safety: 빌드 시도
python .agents/skills/llm-wiki/scripts/graph/graph-build.py >/dev/null
out=$(python .agents/skills/llm-wiki/scripts/viz/graph-html.py)
echo "$out" | grep -q '"written"' || { echo "FAIL feat-21"; echo "$out"; exit 1; }
[ -f "../001_Wiki_AI/990_Meta/graph.html" ] || { echo "FAIL feat-21 html missing"; exit 1; }
echo "PASS feat-21 (graph.html 정적 생성)"
