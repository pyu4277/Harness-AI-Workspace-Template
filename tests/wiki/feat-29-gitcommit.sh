#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
HOOK=".git/hooks/post-commit"
[ -f "$HOOK" ] || { echo "FAIL feat-29 post-commit 부재"; exit 1; }
grep -q "wiki ingest" "$HOOK" || { echo "FAIL feat-29 내용"; exit 1; }
# 실행 가능성 스모크 (변경 없음 → 조용히 0)
bash "$HOOK" && echo "PASS feat-29 (post-commit dry ok)"
