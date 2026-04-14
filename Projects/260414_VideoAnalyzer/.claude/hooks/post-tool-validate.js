#!/usr/bin/env node
/**
 * VideoAnalyzer PostToolUse Validator
 * 출력 파일의 품질을 검증한다.
 * - 보고서 내 상대경로 이미지 참조 감지 (base64만 허용)
 * - 절대경로 하드코딩 감지
 */

const fs = require("fs");

const input = JSON.parse(fs.readFileSync("/dev/stdin", "utf-8"));
const toolName = input.tool_name || "";
const toolInput = input.tool_input || {};
const filePath = (toolInput.file_path || "").replace(/\\/g, "/");
const content = toolInput.content || toolInput.new_string || "";

const warnings = [];

// 보고서 파일(.md)에서 상대경로 이미지 참조 감지
if (filePath.endsWith(".md") && filePath.includes("output/")) {
  const relativeImagePattern = /!\[.*?\]\(\.\//g;
  if (relativeImagePattern.test(content)) {
    warnings.push("보고서에 상대경로 이미지 참조가 발견되었습니다. base64 직접 삽입을 사용하세요.");
  }
}

// 절대경로 하드코딩 감지 (Python/JS 파일)
if (filePath.endsWith(".py") || filePath.endsWith(".js")) {
  const absolutePathPattern = /["'][A-Z]:\\|["']\/home\/|["']\/Users\//g;
  if (absolutePathPattern.test(content)) {
    warnings.push("절대경로 하드코딩이 감지되었습니다. 상대경로를 사용하세요.");
  }
}

// subprocess errors="replace" 누락 감지
if (filePath.endsWith(".py")) {
  if (content.includes("subprocess.run") && !content.includes('errors="replace"') && !content.includes("errors='replace'")) {
    warnings.push("subprocess.run에 errors='replace'가 누락되었습니다 (AER-005).");
  }
}

if (warnings.length > 0) {
  const result = {
    decision: "allow",
    reason: `[하네스 경고] ${warnings.join(" | ")}`
  };
  process.stdout.write(JSON.stringify(result));
} else {
  process.stdout.write(JSON.stringify({ decision: "allow" }));
}
