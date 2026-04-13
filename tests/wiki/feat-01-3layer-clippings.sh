#!/usr/bin/env bash
# =============================================================================
# feat-01 -- Clippings/ prefix가 wiki-pdf-stage에서 허용되는지 확인 (IMP-027)
# 목적: ALLOWED_WIKI_PREFIXES 드리프트 수정 회귀 방지
# =============================================================================

set -e

cd "$(dirname "$0")/../.."
HOOK="$(pwd)/.claude/hooks/wiki-pdf-stage.js"

if [ ! -f "$HOOK" ]; then echo "FAIL: hook 부재"; exit 1; fi

# 도움말 출력에서 허용 prefix 목록 확인
helptxt=$(node "$HOOK" 2>&1 || true)

if ! echo "$helptxt" | grep -q "000_Raw/"; then
  echo "FAIL: 000_Raw/ prefix 누락"; exit 1
fi
if ! echo "$helptxt" | grep -q "Clippings/"; then
  echo "FAIL: Clippings/ prefix 누락 (IMP-027 드리프트 미수정)"; exit 1
fi
if ! echo "$helptxt" | grep -q "990_Meta/archive/"; then
  echo "FAIL: 990_Meta/archive/ prefix 누락"; exit 1
fi

echo "PASS feat-01 (3-layer Clippings 드리프트 수정 확인)"
