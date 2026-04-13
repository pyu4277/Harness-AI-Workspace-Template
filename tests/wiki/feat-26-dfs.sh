#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
# DFS: get_neighbors 재귀 호출로 2-hop 탐색 가능성 smoke
SCRIPT=".agents/mcp/wiki-mcp-server.py"
# graph.json 상 첫 노드
NODE=$(python -c "import json,pathlib; g=json.load(open('../001_Wiki_AI/990_Meta/graph.json',encoding='utf-8')); print(g['nodes'][0]['id'] if g['nodes'] else '')")
if [ -z "$NODE" ]; then echo "SKIP feat-26 (graph empty)"; exit 0; fi
out=$(python "$SCRIPT" --once get_neighbors "{\"id\":\"$NODE\"}")
echo "$out" | grep -q '"neighbors"' || { echo "FAIL feat-26"; exit 1; }
echo "PASS feat-26 (get_neighbors -- DFS 기반)"
