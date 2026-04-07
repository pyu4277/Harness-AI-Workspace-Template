#!/bin/bash
# PreToolUse: 허용 폴더 외 파일 쓰기 차단
# 생성: Harness Architect
# 허용 경로: {{ALLOWED_PATHS}}

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); inp=d.get('tool_input',{}); print(inp.get('file_path',''))" 2>/dev/null)

if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" ]]; then
  # 경로 정규화
  NORM=$(echo "$FILE_PATH" | sed 's|\\|/|g' | sed 's|{{PROJECT_PATH_ESCAPED}}/||')

  # 허용 폴더 체크
  ALLOWED=0
  case "$NORM" in
    {{ALLOWED_CASE_PATTERNS}})
      ALLOWED=1 ;;
    CLAUDE.md|code-convention.md|adr.md)
      ALLOWED=1 ;;
  esac

  if [ $ALLOWED -eq 0 ]; then
    echo "{\"decision\": \"block\", \"reason\": \"쓰기 금지 경로: $NORM (허용: {{ALLOWED_PATHS}})\"}"
    exit 2
  fi
fi

echo "{}"
exit 0
