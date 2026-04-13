#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/extract/ast-extractor.py"
F=$(mktemp --suffix=.py)
trap 'rm -f "$F"' EXIT
cat > "$F" <<'EOF'
def foo(): pass
class Bar:
    def baz(self): pass
EOF
out=$(python "$SCRIPT" "$F" 2>&1)
echo "$out" | grep -q '"node_count"' || { echo "FAIL feat-09"; echo "$out"; exit 1; }
echo "$out" | grep -q '"foo"' || { echo "FAIL feat-09 foo missing"; exit 1; }
echo "PASS feat-09 (ast-extractor Python)"
