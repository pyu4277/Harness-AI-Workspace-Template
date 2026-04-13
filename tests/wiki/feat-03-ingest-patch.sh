#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/wiki-ingest.js"
WIKI_ROOT="$(pwd)/../001_Wiki_AI"
# 대상 md 하나
target=$(find "$WIKI_ROOT" -maxdepth 3 -name "*.md" -not -path "*/.obsidian/*" \
  -not -path "*/000_Raw/*" -not -path "*/Clippings/*" -not -path "*/archive/*" \
  | head -1)
[ -z "$target" ] && { echo "SKIP feat-03"; exit 0; }
out=$(WIKI_ROOT="$WIKI_ROOT" node "$SCRIPT" "$target" 2>/dev/null)
# patch_suggestions 각 항목이 action/file/diff 필드 보유
python <<PY
import json
d = json.loads("""$out""")
for p in d.get("patch_suggestions", [])[:3]:
    assert "action" in p and "file" in p and "diff" in p, "patch schema 위반"
print("PASS feat-03 (ingest patch schema)")
PY
