#!/usr/bin/env bash
# S2: graphify-v1 -> v2 수정 -> watch/lifecycle/lint/schema/hook/git
set -u
cd "$(dirname "$0")/../../.."
source tests/wiki/scenarios/_lib/assert.sh
scenario_init "s2" "update-watch-evolution"
trap 'scenario_emit FAIL' ERR

FX="tests/wiki/fixtures"
WIKI_ROOT="$(pwd)/../001_Wiki_AI"

step "1. lifecycle (cross-ref 후보)" bash tests/wiki/feat-05-lifecycle.sh > /dev/null
mark_feat 05

step "2. shortcut 양방향 검증" bash tests/wiki/feat-06-shortcut-validation.sh > /dev/null
mark_feat 06

step "3. wiki-lint" bash tests/wiki/feat-07-lint.sh > /dev/null
mark_feat 07

step "4. schema-evolution" bash tests/wiki/feat-08-schema-evolution.sh > /dev/null
mark_feat 08

step "5. update-watch (smoke)" bash tests/wiki/feat-14-update-watch.sh > /dev/null
mark_feat 14

step "6. wiki-extract-post 훅 존재" assert_file ".claude/hooks/wiki-extract-post.js"
mark_feat 18

step "7. git post-commit 훅 존재" bash tests/wiki/feat-29-gitcommit.sh > /dev/null
mark_feat 29

scenario_emit PASS
