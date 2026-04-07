#!/bin/bash
# PostToolUse: 금지 패턴 감지
# 생성: Harness Architect

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); inp=d.get('tool_input',{}); print(inp.get('file_path',''))" 2>/dev/null)

if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" ]]; then
  if [ -f "$FILE_PATH" ]; then
    # 금지 패턴 검사
    FORBIDDEN=""

    # eval, new Function, document.write
    if grep -qE "(eval\(|new Function\(|document\.write\()" "$FILE_PATH" 2>/dev/null; then
      FORBIDDEN="eval/Function/document.write 사용 감지"
    fi

    # 하드코딩된 시크릿 패턴
    if grep -qiE "(api_key|password|secret|token)\s*[:=]\s*['\"][^'\"]+['\"]" "$FILE_PATH" 2>/dev/null; then
      FORBIDDEN="${FORBIDDEN:+$FORBIDDEN; }하드코딩된 시크릿 감지"
    fi

    {{ADDITIONAL_FORBIDDEN_PATTERNS}}

    if [ -n "$FORBIDDEN" ]; then
      echo "{\"decision\": \"block\", \"reason\": \"금지 패턴 감지: $FORBIDDEN\"}"
      exit 2
    fi
  fi
fi

echo "{}"
exit 0
