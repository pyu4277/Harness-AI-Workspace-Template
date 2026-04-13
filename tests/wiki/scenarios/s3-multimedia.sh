#!/usr/bin/env bash
# S3: 멀티미디어 (audio/image/office) + token budget
set -u
cd "$(dirname "$0")/../../.."
source tests/wiki/scenarios/_lib/assert.sh
scenario_init "s3" "multimedia-ingest"
trap 'scenario_emit FAIL' ERR

FX="tests/wiki/fixtures"

step "1. audio-transcribe (graceful skip 허용)" python .agents/skills/llm-wiki/scripts/extract/audio-transcribe.py "$FX/audio/short-30s.wav" > reports/e2e/s3-audio.json
mark_feat 10

step "2. vision-caption (subagent 위임 JSON)" python .agents/skills/llm-wiki/scripts/extract/vision-caption.py "$FX/image/chart-flow.png" > reports/e2e/s3-vision.json
mark_feat 17

step "3. office-parse docx" python .agents/skills/llm-wiki/scripts/extract/office-parse.py "$FX/office/notes.docx" > reports/e2e/s3-docx.json
mark_feat 19

step "4. office-parse pptx" python .agents/skills/llm-wiki/scripts/extract/office-parse.py "$FX/office/notes.pptx" >> reports/e2e/s3-docx.json
mark_feat 19

step "5. token-budget" bash -c "echo 'short text fits L0' | node .agents/skills/llm-wiki/scripts/token-budget.js > reports/e2e/s3-budget.json"
mark_feat 20

scenario_emit PASS
