#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
out=$(python .agents/mcp/wiki-mcp-server.py --once search_bm25 '{"query":"AI"}' 2>&1)
echo "$out" | grep -q '"tool": "search_bm25"' || { echo "FAIL feat-28"; echo "$out"; exit 1; }
echo "PASS feat-28 (MCP search_bm25 위임)"
