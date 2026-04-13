#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/extract/pdf-cite.py"
F=$(mktemp --suffix=.txt)
trap 'rm -f "$F"' EXIT
cat > "$F" <<'EOF'
According to [Smith, 2020] and (Jones, 2019), doi:10.1234/abc.2020
arXiv:2106.09685 is also relevant.
EOF
out=$(python "$SCRIPT" "$F")
echo "$out" | grep -q '"citation_count"' || { echo "FAIL feat-11"; exit 1; }
cnt=$(python -c "import json,sys; d=json.loads(sys.argv[1]); print(d['citation_count'])" "$out")
if [ "$cnt" -lt 3 ]; then echo "FAIL feat-11 citations < 3 ($cnt)"; exit 1; fi
echo "PASS feat-11 (pdf-cite citations=$cnt)"
