#!/usr/bin/env bash
# post_tool_validate.sh -- 금지 표현, 허위사실, 인용 누락 감지 (프로젝트 루트 승격 버전)
# Write/Edit 후 실행. 경고성 (exit 0) -- 치명 위반만 exit 2
# 회차 패턴: 260414_[0-9]+차/output/(자소서|이력서|포트폴리오).md

set -euo pipefail
INPUT="$(cat)"

FILE_PATH=$(echo "$INPUT" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# output/ 3종에만 엄격 검증
if ! echo "$FILE_PATH" | grep -qE "260414_[0-9]+차/output/(자소서|이력서|포트폴리오)\.md"; then
  exit 0
fi

BODY=$(cat "$FILE_PATH")

# Rule 1: 금지 과장 표현
FORBIDDEN='(모든\s|항상\s|완벽[한하]|최고의|최상의|최대의|업계\s*1위|역대급|최초로)'
if echo "$BODY" | grep -qE "$FORBIDDEN"; then
  echo "[WARN] forbidden hyperbole detected in $FILE_PATH" >&2
  echo "$BODY" | grep -nE "$FORBIDDEN" | head -5 >&2
fi

# Rule 2: 자기비하 표현
SELF_DEPRECATE='(감히|외람[되되]|~*에\s*불과|미천[한하])'
if echo "$BODY" | grep -qE "$SELF_DEPRECATE"; then
  echo "[WARN] self-deprecating phrasing detected in $FILE_PATH" >&2
fi

# Rule 3: 수치 주장에 인용 누락 감지
NUMERIC_LINES=$(echo "$BODY" | grep -nE "[0-9]+(\.[0-9]+)?\s*(%|배|억|만원|위|명|점)" || true)
if [ -n "$NUMERIC_LINES" ]; then
  while IFS= read -r line; do
    if ! echo "$line" | grep -qE "\[\^(ev|rs)_?[a-zA-Z0-9_]+\]"; then
      echo "[WARN] numeric claim without citation in $FILE_PATH: $line" >&2
    fi
  done <<< "$NUMERIC_LINES"
fi

# Rule 4: 이모티콘 차단 (치명)
if echo "$BODY" | grep -qE "[😀-🙏✨🎉💪🌟]" ; then
  echo "[BLOCKED] emoji detected -- not allowed per CLAUDE.md" >&2
  exit 2
fi

exit 0
