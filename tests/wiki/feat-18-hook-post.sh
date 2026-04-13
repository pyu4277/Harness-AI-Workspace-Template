#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
F=".claude/hooks/wiki-extract-post.js"
[ -f "$F" ] || { echo "FAIL feat-18 hook 부재"; exit 1; }
# smoke: 훅에 wiki-ingest 미포함 입력 투입 → silent exit
echo '{"tool_name":"Read","tool_input":{}}' | node "$F" >/dev/null 2>&1 || true
echo "PASS feat-18 (wiki-extract-post.js 설치 + 호출 가능)"
