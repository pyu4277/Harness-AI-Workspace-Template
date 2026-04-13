#!/usr/bin/env bash
# =============================================================================
# feat-07 -- wiki-lint.js 실행 → JSON 리포트 형식 검증
#   CRITICAL=0 을 강요하지 않는다 (현재 위키 상태를 그대로 리포트해야 함).
#   스키마 유효성(키 존재 여부)만 엄격 검증.
# =============================================================================

set -e

cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/wiki-lint.js"
WIKI_ROOT="$(pwd)/../001_Wiki_AI"

if [ ! -f "$SCRIPT" ]; then echo "FAIL: $SCRIPT 부재"; exit 1; fi

out=$(node "$SCRIPT" "$WIKI_ROOT" 2>/dev/null || true)
if [ -z "$out" ]; then echo "FAIL: lint 출력 없음"; exit 1; fi

for key in '"total_issues"' '"by_severity"' '"issues"' '"timestamp"'; do
  if ! echo "$out" | grep -q "$key"; then
    echo "FAIL: lint JSON 키 누락: $key"; exit 1
  fi
done

echo "PASS feat-07 (wiki-lint 리포트 스키마 유효)"
