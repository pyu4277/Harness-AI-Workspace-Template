#!/usr/bin/env bash
# pre_tool_guard.sh -- Write/Edit 경로 및 회차 불변성 검증 (프로젝트 루트 승격 버전)
# 입력: stdin JSON (tool_name, tool_input.file_path)
# 출력: exit 0 통과 / exit 2 차단 (stderr 사유)
# 회차 패턴: 260414_[0-9]+차/ (최신 회차 = active, 이전 회차 = archived)

set -euo pipefail
INPUT="$(cat)"

FILE_PATH=$(echo "$INPUT" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Rule 1: evidence_vault/ 쓰기 경고 (loose 모드 -- 정식 버전에서 BLOCK 권장)
if echo "$FILE_PATH" | grep -q "evidence_vault/"; then
  echo "[WARN] evidence_vault/ should be immutable after registration. Confirm this is an intentional re-registration." >&2
fi

# Rule 2: 회차 불변성 (이전 회차 수정 경고)
if echo "$FILE_PATH" | grep -qE "260414_[0-9]+차/"; then
  TARGET_ROUND=$(echo "$FILE_PATH" | sed -nE 's|.*260414_([0-9]+)차/.*|\1|p' | head -1)
  # 프로젝트 루트 (Student_Admission_AI) 하위에서 최신 회차 탐지
  PROJECT_ROOT=$(pwd)
  MAX_ROUND=$(ls -d "$PROJECT_ROOT"/260414_*차/ 2>/dev/null | sed -nE 's|.*/260414_([0-9]+)차/?$|\1|p' | sort -n | tail -1)
  MAX_ROUND=${MAX_ROUND:-0}
  if [ -n "$TARGET_ROUND" ] && [ "$MAX_ROUND" -gt 0 ] && [ "$TARGET_ROUND" -lt "$MAX_ROUND" ]; then
    echo "[WARN] 260414_${TARGET_ROUND}차 is archived (current active: 260414_${MAX_ROUND}차). Consider creating a new round instead of modifying archived one." >&2
  fi
fi

# Rule 3: 파일명 규칙 (research_cache/ 안의 파일은 YYMMDD_ 또는 summary.md / INDEX.md)
if echo "$FILE_PATH" | grep -qE "research_cache/"; then
  BASENAME=$(basename "$FILE_PATH")
  if ! echo "$BASENAME" | grep -qE "^([0-9]{6}_|summary\.md$|INDEX\.md$)"; then
    echo "[WARN] research file should start with YYMMDD_: $BASENAME" >&2
  fi
fi

# Rule 4: 절대경로 하드코딩 금지 (content 검사)
CONTENT=$(echo "$INPUT" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('tool_input',{}).get('content',''))" 2>/dev/null || echo "")
if echo "$CONTENT" | grep -qE "(D:/|C:/|/Users/|/home/)" ; then
  echo "[WARN] absolute path detected in content -- use relative paths." >&2
fi

exit 0
