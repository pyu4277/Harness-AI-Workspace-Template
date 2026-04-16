#!/usr/bin/env bash
# pre_mcp_pii_guard.sh -- 외부 MCP 호출 시 PII / evidence_vault 경로 포함 차단
# 입력: stdin JSON (tool_input)
# 출력: exit 0 통과 / exit 2 차단

set -euo pipefail
INPUT="$(cat)"

PARAMS=$(echo "$INPUT" | python -c "import sys,json;d=json.load(sys.stdin);import json as j;print(j.dumps(d.get('tool_input',{})))" 2>/dev/null || echo "{}")

# Rule 1: evidence_vault/ 경로가 파라미터에 포함되면 차단
if echo "$PARAMS" | grep -q "evidence_vault"; then
  echo "[BLOCKED] evidence_vault/ contents must not be sent to external MCP (PII)." >&2
  exit 2
fi

# Rule 2: 전형적 PII 패턴 (한글 이름 + 숫자 연속) -- 보수적 차단
if echo "$PARAMS" | grep -qE "[가-힣]{2,4}\s*[0-9]{6,}"; then
  echo "[BLOCKED] suspected PII pattern (name + ID/phone). Sanitize query." >&2
  exit 2
fi

# Rule 3: 주민등록번호 패턴 차단
if echo "$PARAMS" | grep -qE "[0-9]{6}[-][1-4][0-9]{6}"; then
  echo "[BLOCKED] RRN detected. Remove from query." >&2
  exit 2
fi

# Rule 4: 이메일 차단
if echo "$PARAMS" | grep -qE "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"; then
  echo "[BLOCKED] email in query. Remove before sending to external MCP." >&2
  exit 2
fi

exit 0
