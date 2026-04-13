#!/usr/bin/env bash
# =============================================================================
# Phase 0 PromptRefinementGate -- end-to-end 검증
# 기대 동작: glossary 매칭 → stderr HINT + refine-log.jsonl 라인 +1
# =============================================================================

set -e

cd "$(dirname "$0")/../.."  # 005_AI_Project 루트
PROJECT_ROOT="$(pwd)"

HOOK="$PROJECT_ROOT/.claude/hooks/prompt-refiner.js"
LOG="$PROJECT_ROOT/.harness/refine-log.jsonl"
GLOSSARY="$PROJECT_ROOT/docs/LogManagement/용어사전.md"

if [ ! -f "$HOOK" ]; then
  echo "FAIL: hook 없음 $HOOK"; exit 1
fi
if [ ! -f "$GLOSSARY" ]; then
  echo "SKIP: 용어사전 부재 (테스트 전제 불충족) $GLOSSARY"; exit 0
fi

before=0
if [ -f "$LOG" ]; then
  before=$(grep -c . "$LOG" || echo 0)
fi

# 용어사전 원문 칼럼에서 첫 번째 4자 이상 표현 하나 추출
sample_original=$(awk -F'|' 'NF>=3 {
  t=$2; o=$3;
  gsub(/^[ \t]+|[ \t]+$/, "", t);
  gsub(/^[ \t]+|[ \t]+$/, "", o);
  if (length(o) >= 4 && o != "원문" && t != o) { print o; exit }
}' "$GLOSSARY")

if [ -z "$sample_original" ]; then
  echo "SKIP: 용어사전에 4자 이상 원문 없음"; exit 0
fi

# 훅 실행 (stdin JSON 투입)
stderr_out=$(printf '%s' "{\"message\":\"$sample_original 를 처리해줘\"}" \
  | node "$HOOK" 2>&1 >/dev/null || true)

if ! echo "$stderr_out" | grep -q "HINT"; then
  echo "FAIL: stderr HINT 누락"
  echo "--- stderr ---"; echo "$stderr_out"
  exit 1
fi

after=0
if [ -f "$LOG" ]; then
  after=$(grep -c . "$LOG" || echo 0)
fi

if [ "$after" -le "$before" ]; then
  echo "FAIL: refine-log 라인 증가 없음 (before=$before after=$after)"
  exit 1
fi

echo "PASS phase0-gate (before=$before after=$after)"
