#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
F="../001_Wiki_AI/990_Meta/GRAPH_REPORT.md"
[ -f "$F" ] || { echo "FAIL feat-23 template 부재"; exit 1; }
grep -q "schema_version: 2" "$F" || { echo "FAIL feat-23 schema_version"; exit 1; }
grep -q "graph.json" "$F" || { echo "FAIL feat-23 graph.json ref"; exit 1; }
echo "PASS feat-23 (GRAPH_REPORT.md template)"
