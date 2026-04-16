#!/usr/bin/env node
/**
 * VideoAnalyzer PreToolUse Guard
 * 입력/프레임 디렉토리 쓰기를 구조적으로 차단한다.
 */

const fs = require("fs");

const input = JSON.parse(fs.readFileSync("/dev/stdin", "utf-8"));
const toolName = input.tool_name || "";
const toolInput = input.tool_input || {};
const filePath = (toolInput.file_path || toolInput.path || "").replace(/\\/g, "/").toLowerCase();

// 보호 대상 경로
const PROTECTED_PATHS = [
  "input/video",
  "input/subtitle",
  "input/audio",
  "workspace/frames"
];

// Write/Edit 도구에서 보호 경로 쓰기 차단
if (toolName === "Write" || toolName === "Edit") {
  for (const protectedPath of PROTECTED_PATHS) {
    if (filePath.includes(protectedPath)) {
      const result = {
        decision: "block",
        reason: `[하네스] ${protectedPath}/ 는 읽기 전용입니다. 쓰기가 차단되었습니다.`
      };
      process.stdout.write(JSON.stringify(result));
      process.exit(0);
    }
  }
}

// 통과
process.stdout.write(JSON.stringify({ decision: "allow" }));
