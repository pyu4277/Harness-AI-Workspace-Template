#!/usr/bin/env bash
# =============================================================================
# feat-02 -- CLAUDE.md schema_version 필드 존재 확인
# =============================================================================

set -e

cd "$(dirname "$0")/../.."
WIKI_CLAUDE="../001_Wiki_AI/CLAUDE.md"

if [ ! -f "$WIKI_CLAUDE" ]; then echo "FAIL: $WIKI_CLAUDE 부재"; exit 1; fi

if ! grep -q "schema_version:\s*2" "$WIKI_CLAUDE"; then
  echo "FAIL: schema_version: 2 필드 누락"; exit 1
fi

echo "PASS feat-02 (schema_version: 2 필드 확인)"
