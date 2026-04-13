#!/usr/bin/env bash
# =============================================================================
# feat-05 -- wiki-ingest.js 가 10-15개 관련 페이지 후보 + patch JSON 출력
#   (후보 부족 시 WARN만 내고 비제로 exit 금지)
# =============================================================================

set -e

cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/wiki-ingest.js"
WIKI_ROOT="$(pwd)/../001_Wiki_AI"

if [ ! -f "$SCRIPT" ]; then echo "FAIL: $SCRIPT 부재"; exit 1; fi

# 임의 타겟: WIKI_ROOT 내 첫 번째 md 파일 (루트 제외)
target=$(find "$WIKI_ROOT" -maxdepth 3 -name "*.md" -not -path "*/.obsidian/*" \
  -not -path "*/000_Raw/*" -not -path "*/Clippings/*" -not -path "*/archive/*" \
  | head -2 | tail -1)

if [ -z "$target" ]; then
  echo "SKIP: wiki 내 md 파일 없음"; exit 0
fi

out=$(WIKI_ROOT="$WIKI_ROOT" node "$SCRIPT" "$target" 2>/dev/null || true)

if [ -z "$out" ]; then echo "FAIL: wiki-ingest 출력 없음"; exit 1; fi

# JSON 파싱 + related 배열 길이 확인
cnt=$(node -e "
const j = JSON.parse(process.argv[1]);
console.log((j.related || []).length);
" "$out" 2>/dev/null || echo 0)

if ! echo "$out" | grep -q '"patch_suggestions"'; then
  echo "FAIL: patch_suggestions 키 누락"; exit 1
fi
if ! echo "$out" | grep -q '"related"'; then
  echo "FAIL: related 키 누락"; exit 1
fi

echo "PASS feat-05 (lifecycle 후보 $cnt 개 + patch_suggestions 생성)"
