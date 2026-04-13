#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
SCRIPT=".agents/skills/llm-wiki/scripts/wiki-lint.js"
WIKI_ROOT="$(pwd)/../001_Wiki_AI"
# 임시 shortcut 파일 — 존재하지 않는 canonical 가리킴 → lint 가 SHORTCUT_ORPHAN 검출해야
TMP="$WIKI_ROOT/100_Philosophy/concepts/_shortcut_probe.md"
mkdir -p "$(dirname "$TMP")"
cat > "$TMP" <<EOF
---
title: "probe shortcut"
type: shortcut
canonical: "010_Verified/sources/_nonexistent_V001.md"
created: 2026-04-13
---
body
EOF
trap 'rm -f "$TMP"' EXIT
out=$(node "$SCRIPT" "$WIKI_ROOT" 2>/dev/null || true)
echo "$out" | grep -q "SHORTCUT_ORPHAN" || { echo "FAIL feat-06"; exit 1; }
echo "PASS feat-06 (shortcut 양방향 검증)"
