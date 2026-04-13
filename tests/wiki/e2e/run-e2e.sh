#!/usr/bin/env bash
# 6 시나리오 병렬 오케스트레이터. xargs -P6.
set -u
cd "$(dirname "$0")/../../.."
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
mkdir -p reports/e2e

PARALLEL=6
PDCA=0
for arg in "$@"; do
  case "$arg" in
    --parallel=*) PARALLEL="${arg#*=}" ;;
    --parallel) shift ;;
    --pdca) PDCA=1 ;;
  esac
done

T0=$(date +%s)
echo "==== E2E PDCA Run (parallel=$PARALLEL pdca=$PDCA) ===="

# 시나리오 목록
SCENS=(s1 s2 s3 s4 s5 s6)

# 병렬 실행 (background + wait)
pids=()
for s in "${SCENS[@]}"; do
  bash "tests/wiki/scenarios/${s}-"*.sh > "reports/e2e/${s}.log" 2>&1 &
  pids+=($!)
  echo "  spawned $s pid=${pids[-1]}"
done

failed=0
for i in "${!SCENS[@]}"; do
  if wait "${pids[$i]}"; then
    echo "  [OK ] ${SCENS[$i]}"
  else
    echo "  [ERR] ${SCENS[$i]} (rc=$?)"
    failed=$((failed+1))
  fi
done

T1=$(date +%s)
WALL=$((T1-T0))
echo ""
echo "==== Wall time: ${WALL}s, failed=$failed/${#SCENS[@]} ===="

# 집계
python tests/wiki/e2e/coverage-check.py
python tests/wiki/e2e/gap-report.py

if [ "$failed" -gt 0 ]; then
  exit 1
fi
