#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/mcp/wiki-mcp-server.py"
out=$(python "$SCRIPT" --once query_graph '{}')
echo "$out" | grep -q '"node_count"' || { echo "FAIL feat-22 query_graph"; echo "$out"; exit 1; }
out2=$(python "$SCRIPT" --once get_neighbors '{"id":"does_not_exist"}')
echo "$out2" | grep -q '"neighbors"' || { echo "FAIL feat-22 get_neighbors"; exit 1; }
echo "PASS feat-22 (wiki-mcp-server tools)"
