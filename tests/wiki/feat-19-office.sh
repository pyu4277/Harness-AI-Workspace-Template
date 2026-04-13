#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/extract/office-parse.py"
F="tests/wiki/fixtures/_tmp_probe.docx"
mkdir -p tests/wiki/fixtures
trap 'rm -f "$F"' EXIT
python - <<PY
import zipfile
with zipfile.ZipFile("$F", "w") as z:
    z.writestr("word/document.xml",
      "<w:document><w:body><w:p><w:r><w:t>hello harness</w:t></w:r></w:p></w:body></w:document>")
PY
out=$(python "$SCRIPT" "$F")
echo "$out" | grep -q '"kind": "docx"' || { echo "FAIL feat-19 kind"; echo "$out"; exit 1; }
echo "$out" | grep -q "hello harness" || { echo "FAIL feat-19 text"; echo "$out"; exit 1; }
echo "PASS feat-19 (office-parse docx)"
