#!/usr/bin/env bash
# 공용 어설션 라이브러리. 모든 시나리오는 이 lib 를 source 한다.
set -u
SCENARIO_T0=$(date +%s)
SCENARIO_FEATS=()
SCENARIO_STEPS=()

scenario_init() {
  SCENARIO_ID="$1"
  SCENARIO_NAME="$2"
  echo "==[$SCENARIO_ID] $SCENARIO_NAME =="
  export PYTHONUTF8=1
  export PYTHONIOENCODING=utf-8
}

step() {
  local desc="$1"; shift
  echo "  -> $desc"
  if "$@"; then
    SCENARIO_STEPS+=("PASS:$desc")
  else
    SCENARIO_STEPS+=("FAIL:$desc")
    return 1
  fi
}

mark_feat() {
  for f in "$@"; do SCENARIO_FEATS+=("$f"); done
}

assert_file() { [ -f "$1" ] || { echo "    [FAIL] missing: $1"; return 1; }; }
assert_grep() { grep -q "$1" "$2" || { echo "    [FAIL] '$1' not in $2"; return 1; }; }
assert_not_empty() { [ -s "$1" ] || { echo "    [FAIL] empty: $1"; return 1; }; }

scenario_emit() {
  local status="$1"
  local t1=$(date +%s)
  local elapsed=$((t1 - SCENARIO_T0))
  local feats=$(printf '"%s",' "${SCENARIO_FEATS[@]+"${SCENARIO_FEATS[@]}"}" | sed 's/,$//')
  local steps=$(printf '"%s",' "${SCENARIO_STEPS[@]+"${SCENARIO_STEPS[@]}"}" | sed 's/,$//')
  mkdir -p reports/e2e
  cat > "reports/e2e/${SCENARIO_ID}.json" <<JSON
{
  "id": "$SCENARIO_ID",
  "name": "$SCENARIO_NAME",
  "status": "$status",
  "elapsed_s": $elapsed,
  "feats": [$feats],
  "steps": [$steps],
  "ts": "$(date -Is 2>/dev/null || date)"
}
JSON
  echo "==[$SCENARIO_ID] $status (${elapsed}s) -> reports/e2e/${SCENARIO_ID}.json"
}
