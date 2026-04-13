#!/usr/bin/env bash
# =============================================================================
# run-all.sh -- 33 테스트 (phase0 + feat-01~32) 순차 실행 + 매트릭스 생성
# 실패 허용 0건: 하나라도 실패하면 exit 1.
# 생성: ../001_Wiki_AI/990_Meta/verification-matrix.md
# =============================================================================

set -u
cd "$(dirname "$0")/../.."

MATRIX="../001_Wiki_AI/990_Meta/verification-matrix.md"
TMP="/tmp/verif-matrix.$$.md"

mkdir -p "$(dirname "$MATRIX")"

pass=0; fail=0; skipped=0; total=0
declare -a results

run_one() {
  local f="$1"
  local name
  name=$(basename "$f" .sh)
  local t0 t1 elapsed status msg
  t0=$(python -c "import time; print(time.time())")
  local out
  out=$(bash "$f" 2>&1) && status="PASS" || status="FAIL"
  t1=$(python -c "import time; print(time.time())")
  elapsed=$(python -c "print(f'{$t1 - $t0:.2f}')")
  msg=$(echo "$out" | tail -1)
  total=$((total + 1))
  if [ "$status" = "PASS" ]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
  fi
  results+=("| $name | $status | ${elapsed}s | ${msg//|/\\|} |")
}

tests=(
  tests/wiki/phase0-gate.sh
  tests/wiki/feat-01-3layer-clippings.sh
  tests/wiki/feat-02-schema-version.sh
  tests/wiki/feat-03-ingest-patch.sh
  tests/wiki/feat-04-log-event.sh
  tests/wiki/feat-05-lifecycle.sh
  tests/wiki/feat-06-shortcut-validation.sh
  tests/wiki/feat-07-lint.sh
  tests/wiki/feat-08-schema-evolution.sh
  tests/wiki/feat-09-ast.sh
  tests/wiki/feat-10-audio.sh
  tests/wiki/feat-11-pdf-cite.sh
  tests/wiki/feat-12-leiden.sh
  tests/wiki/feat-13-graph-json.sh
  tests/wiki/feat-14-update-watch.sh
  tests/wiki/feat-15-subagent.sh
  tests/wiki/feat-16-cache.sh
  tests/wiki/feat-17-vision.sh
  tests/wiki/feat-18-hook-post.sh
  tests/wiki/feat-19-office.sh
  tests/wiki/feat-20-token-budget.sh
  tests/wiki/feat-21-graph-html.sh
  tests/wiki/feat-22-mcp.sh
  tests/wiki/feat-23-graph-report.sh
  tests/wiki/feat-24-bm25.sh
  tests/wiki/feat-25-3layer.sh
  tests/wiki/feat-26-dfs.sh
  tests/wiki/feat-27-obsidian.sh
  tests/wiki/feat-28-mcp-search.sh
  tests/wiki/feat-29-gitcommit.sh
  tests/wiki/feat-30-daemon.sh
  tests/wiki/feat-31-autodetect.sh
  tests/wiki/feat-32-global.sh
)

for t in "${tests[@]}"; do
  if [ ! -f "$t" ]; then
    echo "MISSING: $t"
    results+=("| $(basename "$t" .sh) | MISSING | - | file not found |")
    fail=$((fail + 1))
    total=$((total + 1))
    continue
  fi
  run_one "$t"
done

{
  echo "---"
  echo "title: \"LLM Wiki 검증 매트릭스\""
  echo "type: analysis"
  echo "domain: 990_Meta"
  echo "schema_version: 2"
  echo "created: $(date -Is 2>/dev/null || date)"
  echo "---"
  echo ""
  echo "# LLM Wiki 검증 매트릭스 (auto-generated)"
  echo ""
  echo "- 총 테스트: $total"
  echo "- PASS: $pass"
  echo "- FAIL: $fail"
  echo "- 생성: $(date -Is 2>/dev/null || date)"
  echo ""
  echo "| Test | Status | Elapsed | Last message |"
  echo "|------|--------|---------|--------------|"
  for line in "${results[@]}"; do echo "$line"; done
} > "$TMP"

mv "$TMP" "$MATRIX"
echo ""
echo "==== SUMMARY ===="
echo "total=$total pass=$pass fail=$fail"
echo "matrix: $MATRIX"

if [ "$fail" -gt 0 ]; then
  exit 1
fi
