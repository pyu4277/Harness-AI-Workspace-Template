#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/wiki-log-append.js"
LOG="../001_Wiki_AI/log.md"
[ -f "$LOG" ] || { echo "SKIP feat-04 (log.md 부재)"; exit 0; }

before=$(grep -c "^| 26" "$LOG" 2>/dev/null || echo 0)
node "$SCRIPT" event INGEST "tests/probe" "phase4 smoke" 2>/dev/null
after=$(grep -c "^| 26" "$LOG" 2>/dev/null || echo 0)

if [ "$after" -le "$before" ]; then
  echo "FAIL feat-04 (event row 추가 안됨: $before -> $after)"; exit 1
fi
# 정리: 추가한 probe 행 제거
python <<PY
from pathlib import Path
p = Path("../001_Wiki_AI/log.md")
text = p.read_text(encoding="utf-8")
lines = [l for l in text.splitlines() if "tests/probe" not in l]
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
echo "PASS feat-04 (log event append $before -> $after)"
