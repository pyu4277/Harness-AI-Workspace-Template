#!/usr/bin/env bash
# S5: 글로벌 registry + obsidian + daemon + autodetect
set -u
cd "$(dirname "$0")/../../.."
source tests/wiki/scenarios/_lib/assert.sh
scenario_init "s5" "multi-project-global"
trap 'scenario_emit FAIL' ERR

step "1. obsidian 양방향" bash tests/wiki/feat-27-obsidian.sh > /dev/null
mark_feat 27

step "2. daemon-5min --once" bash tests/wiki/feat-30-daemon.sh > /dev/null
mark_feat 30

step "3. LLM autodetect 우선순위" bash tests/wiki/feat-31-autodetect.sh > /dev/null
mark_feat 31

step "4. global wiki-registry 검증" bash tests/wiki/feat-32-global.sh > /dev/null
mark_feat 32

scenario_emit PASS
