#!/usr/bin/env bash
# S1: PDF + 3 md 투입 -> ingest -> graph -> BM25 -> html viz
set -u
cd "$(dirname "$0")/../../.."
source tests/wiki/scenarios/_lib/assert.sh
scenario_init "s1" "happy-path-karpathy"
trap 'scenario_emit FAIL' ERR

FX="tests/wiki/fixtures"
WIKI_ROOT="$(pwd)/../001_Wiki_AI"

step "1. PDF cite extraction" python ".agents/skills/llm-wiki/scripts/extract/pdf-cite.py" "$FX/pdf/karpathy-llm101.pdf"
mark_feat 11

step "2. AST extract on .md" python ".agents/skills/llm-wiki/scripts/extract/ast-extractor.py" "$FX/md/karpathy-excerpt.md" markdown
mark_feat 09

step "3. wiki-ingest patch" bash -c "WIKI_ROOT=\"$WIKI_ROOT\" node .agents/skills/llm-wiki/scripts/wiki-ingest.js \"$FX/md/karpathy-excerpt.md\" > reports/e2e/s1-ingest.json"
mark_feat 03 05

step "4. schema_version 검증" assert_grep "schema_version" "$WIKI_ROOT/CLAUDE.md"
mark_feat 02

step "5. graph-build" bash -c "WIKI_ROOT=\"$WIKI_ROOT\" python .agents/skills/llm-wiki/scripts/graph/graph-build.py > reports/e2e/s1-graph.json"
mark_feat 13

step "6. Leiden cluster (mini graph)" bash -c "echo '{\"nodes\":[{\"id\":\"a\"},{\"id\":\"b\"},{\"id\":\"c\"},{\"id\":\"d\"}],\"edges\":[{\"src\":\"a\",\"dst\":\"b\"},{\"src\":\"c\",\"dst\":\"d\"}]}' | python .agents/skills/llm-wiki/scripts/graph/leiden-cluster.py > reports/e2e/s1-leiden.json"
mark_feat 12

step "7. graph-html viz" bash -c "WIKI_ROOT=\"$WIKI_ROOT\" python .agents/skills/llm-wiki/scripts/viz/graph-html.py > /dev/null"
mark_feat 21

step "8. BM25 query" bash -c "WIKI_ROOT=\"$WIKI_ROOT\" PYTHONIOENCODING=utf-8 python .agents/skills/llm-wiki/scripts/wiki-query.py 'transformer attention' --layer 0 --top-k 5 > reports/e2e/s1-bm25.json"
mark_feat 24

step "9. GRAPH_REPORT 존재" assert_file "$WIKI_ROOT/990_Meta/GRAPH_REPORT.md"
mark_feat 23

step "10. Clippings prefix 통과" bash tests/wiki/feat-01-3layer-clippings.sh > /dev/null
mark_feat 01

scenario_emit PASS
