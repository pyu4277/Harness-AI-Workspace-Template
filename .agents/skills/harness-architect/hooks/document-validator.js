#!/usr/bin/env node
// PostToolUse(Write): 생성된 문서의 기본 품질 검증
// - 빈 파일 아닌지
// - Markdown 헤딩 존재
// - 한국어 포함 (응답 규칙)
// - CLAUDE.md인 경우 줄 수 제한

const fs = require('fs');

async function main() {
  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  try {
    const data = JSON.parse(input);

    if (data.tool_name !== 'Write' && data.tool_name !== 'Edit') {
      process.stdout.write('{}');
      process.exit(0);
    }

    const filePath = data.tool_input?.file_path || '';

    // MD/JSON 파일만 검증
    if (!filePath.endsWith('.md') && !filePath.endsWith('.json')) {
      process.stdout.write('{}');
      process.exit(0);
    }

    if (!fs.existsSync(filePath)) {
      process.stdout.write('{}');
      process.exit(0);
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const warnings = [];

    // 1. 빈 파일 체크
    if (content.trim().length === 0) {
      warnings.push('빈 파일이 생성되었습니다');
    }

    // 2. CLAUDE.md 줄 수 제한
    if (filePath.endsWith('CLAUDE.md')) {
      const lineCount = content.split('\n').length;
      if (lineCount > 500) {
        // 500줄 초과: 차단
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: `CLAUDE.md가 ${lineCount}줄입니다. 500줄 이하로 줄여야 합니다. (권장: 60줄 이하)`
        }));
        process.exit(2);
      }
      if (lineCount > 60) {
        warnings.push(`CLAUDE.md가 ${lineCount}줄입니다. 60줄 이하 권장.`);
      }
    }

    // 3. Markdown 헤딩 존재 확인 (MD 파일)
    if (filePath.endsWith('.md') && content.trim().length > 0) {
      if (!content.match(/^#+ /m)) {
        warnings.push('Markdown 헤딩(#)이 없습니다');
      }
    }

    // 경고가 있으면 메시지로 전달 (차단하지 않음)
    if (warnings.length > 0) {
      process.stdout.write(JSON.stringify({
        warnings: warnings
      }));
    } else {
      process.stdout.write('{}');
    }
  } catch {
    process.stdout.write('{}');
  }

  process.exit(0);
}

main();
