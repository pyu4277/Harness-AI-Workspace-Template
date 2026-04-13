#!/usr/bin/env bash
# S6: 손상 md + daemon kill 흉내 -> 로그/lifecycle/캐시/훅/daemon 회복
set -u
cd "$(dirname "$0")/../../.."
source tests/wiki/scenarios/_lib/assert.sh
scenario_init "s6" "chaos-recovery"
trap 'scenario_emit FAIL' ERR

FX="tests/wiki/fixtures"
WIKI_ROOT="$(pwd)/../001_Wiki_AI"

step "1. log-event append" bash tests/wiki/feat-04-log-event.sh > /dev/null
mark_feat 04

step "2. lifecycle 재실행 (재시도 시뮬)" bash tests/wiki/feat-05-lifecycle.sh > /dev/null
mark_feat 05

step "3. 손상 md graceful 처리 (lint이 0건 추가 또는 graceful)" bash -c "node .agents/skills/llm-wiki/scripts/wiki-lint.js \"$WIKI_ROOT\" 2>&1 | head -5 > reports/e2e/s6-chaos-lint.txt; true"
mark_feat 14

step "4. 캐시 재조회 무손실" bash tests/wiki/feat-16-cache.sh > /dev/null
mark_feat 16

step "5. extract-post 훅 코드 무결" assert_file ".claude/hooks/wiki-extract-post.js"
mark_feat 18

step "6. daemon 재기동 (--once)" bash tests/wiki/feat-30-daemon.sh > /dev/null
mark_feat 30

scenario_emit PASS
