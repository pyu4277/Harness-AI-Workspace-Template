#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/graph/graph-build.py"
out=$(python "$SCRIPT" 2>&1)
echo "$out" | grep -q '"written"' || { echo "FAIL feat-13"; echo "$out"; exit 1; }
GRAPH="../001_Wiki_AI/990_Meta/graph.json"
[ -f "$GRAPH" ] || { echo "FAIL feat-13 graph.json missing"; exit 1; }
python -c "import json; d=json.load(open('$GRAPH',encoding='utf-8')); assert 'nodes' in d and 'edges' in d; print('nodes', len(d['nodes']))"
echo "PASS feat-13 (graph.json 생성)"
