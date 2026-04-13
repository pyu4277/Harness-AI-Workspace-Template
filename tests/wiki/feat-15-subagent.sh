#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../.."
F=".agents/subagents/semantic-extractor.md"
[ -f "$F" ] || { echo "FAIL feat-15 subagent 부재"; exit 1; }
grep -q "name: semantic-extractor" "$F" || { echo "FAIL feat-15 name"; exit 1; }
grep -q '```mermaid' "$F" || { echo "FAIL feat-15 mermaid"; exit 1; }
grep -q "Output Schema" "$F" || { echo "FAIL feat-15 schema"; exit 1; }
echo "PASS feat-15 (semantic-extractor subagent)"
