#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/graph/leiden-cluster.py"
input='{"nodes":["a","b","c","d","e","f","g","h","i","j"],
"edges":[["a","b"],["b","c"],["a","c"],["d","e"],["e","f"],["d","f"],["g","h"],["h","i"],["i","j"],["g","i"]]}'
out=$(printf '%s' "$input" | python "$SCRIPT")
echo "$out" | grep -q '"n_communities"' || { echo "FAIL feat-12"; echo "$out"; exit 1; }
n=$(python -c "import json,sys; d=json.loads(sys.argv[1]); print(d['n_communities'])" "$out")
if [ "$n" -lt 2 ]; then echo "FAIL feat-12 communities<2 ($n)"; exit 1; fi
echo "PASS feat-12 (leiden n_communities=$n)"
