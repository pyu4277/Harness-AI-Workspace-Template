#!/usr/bin/env bash
# post_round_check.sh -- Stop 훅. 세션 종료 시 현재 active 회차 완결성 검증.
# 경고성. 실패해도 세션 종료 진행.
# 회차 패턴: 260414_[0-9]+차/ (프로젝트 루트 기준)

set -euo pipefail

# 프로젝트 루트 (현재 cwd) 하위에서 최신 회차 탐지
CURRENT=$(ls -d 260414_*차/ 2>/dev/null | sed -nE 's|260414_([0-9]+)차/?|\1|p' | sort -n | tail -1 || echo "")

if [ -z "$CURRENT" ]; then
  exit 0
fi

DIR="260414_${CURRENT}차"
MISSING=()

# 필수 폴더/파일 체크
[ -d "$DIR/input" ]         || MISSING+=("$DIR/input/")
[ -d "$DIR/output" ]        || MISSING+=("$DIR/output/")
[ -f "$DIR/company_profile.md" ] || MISSING+=("$DIR/company_profile.md")
[ -f "$DIR/ideas.md" ]      || MISSING+=("$DIR/ideas.md")

# 2차 이상이면 CHANGELOG 필수
if [ "$CURRENT" -ge 2 ]; then
  [ -f "$DIR/CHANGELOG.md" ] || MISSING+=("$DIR/CHANGELOG.md (required for N>=2)")
fi

# output 3종 완결 여부
OUTPUT_MISSING=()
[ -f "$DIR/output/자소서.md" ] || OUTPUT_MISSING+=("자소서.md")
[ -f "$DIR/output/이력서.md" ] || OUTPUT_MISSING+=("이력서.md")
[ -f "$DIR/output/포트폴리오.md" ] || OUTPUT_MISSING+=("포트폴리오.md")

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "[ROUND_CHECK] 260414_${CURRENT}차 누락 (구조적 필수):" >&2
  printf '  - %s\n' "${MISSING[@]}" >&2
fi

if [ ${#OUTPUT_MISSING[@]} -gt 0 ]; then
  echo "[ROUND_CHECK] 260414_${CURRENT}차 output/ 미완성:" >&2
  printf '  - %s\n' "${OUTPUT_MISSING[@]}" >&2
fi

exit 0
