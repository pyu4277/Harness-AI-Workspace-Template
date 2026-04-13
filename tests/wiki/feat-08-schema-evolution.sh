#!/usr/bin/env bash
# =============================================================================
# feat-08 -- schema-diff 체크 동작 확인
#   임시 md (schema_version: 1 frontmatter) 를 WIKI_ROOT 하위에 만들고
#   lint 실행 시 SCHEMA_DIFF 이슈가 출력되는지 검증 → 테스트 후 정리.
# =============================================================================

set -e

cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/wiki-lint.js"
WIKI_ROOT="$(pwd)/../001_Wiki_AI"

if [ ! -f "$SCRIPT" ]; then echo "FAIL: $SCRIPT 부재"; exit 1; fi

# 테스트 대상: 도메인 하위에 임시 v1 페이지 배치
DOMAIN_DIR="$WIKI_ROOT/100_Philosophy/concepts"
mkdir -p "$DOMAIN_DIR"
TMP="$DOMAIN_DIR/_schema_diff_probe.md"

cat > "$TMP" <<EOF
---
title: "schema-diff probe"
domain: 100_Philosophy
type: concept
schema_version: 1
created: 2026-04-13
updated: 2026-04-13
---

probe body
EOF

cleanup() { rm -f "$TMP"; }
trap cleanup EXIT

out=$(node "$SCRIPT" "$WIKI_ROOT" 2>/dev/null || true)

if ! echo "$out" | grep -q 'SCHEMA_DIFF'; then
  echo "FAIL: SCHEMA_DIFF 이슈 감지 실패"
  exit 1
fi

echo "PASS feat-08 (schema-diff v1 감지)"
