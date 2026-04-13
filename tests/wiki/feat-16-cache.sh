#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/cache/sha256-cache.py"
F=$(mktemp --suffix=.txt)
trap 'rm -f "$F"' EXIT
echo "unique-content-$RANDOM" > "$F"

out1=$(python "$SCRIPT" check "$F")
hit1=$(python -c "import json,sys; print(json.loads(sys.argv[1])['hit'])" "$out1")
[ "$hit1" = "False" ] || { echo "FAIL feat-16 first miss expected"; exit 1; }

python "$SCRIPT" put "$F" >/dev/null
out2=$(python "$SCRIPT" check "$F")
hit2=$(python -c "import json,sys; print(json.loads(sys.argv[1])['hit'])" "$out2")
[ "$hit2" = "True" ] || { echo "FAIL feat-16 second hit expected"; exit 1; }

echo "PASS feat-16 (sha256-cache miss→put→hit)"
