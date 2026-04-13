#!/usr/bin/env bash
# S4: MCP search loop + cache + DFS + 3-layer
set -u
cd "$(dirname "$0")/../../.."
source tests/wiki/scenarios/_lib/assert.sh
scenario_init "s4" "mcp-search-loop"
trap 'scenario_emit FAIL' ERR

WIKI_ROOT="$(pwd)/../001_Wiki_AI"
T0=$(python -c "import time; print(time.time())")

step "1. SHA256 cache check" bash tests/wiki/feat-16-cache.sh > /dev/null
mark_feat 16

step "2. semantic-extractor subagent 정의 존재" assert_file ".agents/subagents/semantic-extractor.md"
mark_feat 15

step "3. MCP query_graph (--once)" bash -c "WIKI_ROOT=\"$WIKI_ROOT\" PYTHONIOENCODING=utf-8 python .agents/mcp/wiki-mcp-server.py --once query_graph '{}' > reports/e2e/s4-mcp1.json"
mark_feat 22

step "4. MCP search_bm25 (--once) + 시간 측정" bash -c "WIKI_ROOT=\"$WIKI_ROOT\" PYTHONIOENCODING=utf-8 python .agents/mcp/wiki-mcp-server.py --once search_bm25 '{\"query\":\"transformer\",\"top_k\":3}' > reports/e2e/s4-mcp2.json"
mark_feat 28

step "5. 3-layer 100-token query" bash -c "WIKI_ROOT=\"$WIKI_ROOT\" PYTHONIOENCODING=utf-8 python .agents/skills/llm-wiki/scripts/wiki-query.py 'transformer' --layer 100 --top-k 3 > reports/e2e/s4-l1.json"
mark_feat 25

step "6. DFS graph 탐색" bash tests/wiki/feat-26-dfs.sh > /dev/null
mark_feat 26

T1=$(python -c "import time; print(time.time())")
ELAPSED=$(python -c "print(f'{$T1 - $T0:.2f}')")
echo "  MCP loop p95 (전체 wall): ${ELAPSED}s"

scenario_emit PASS
