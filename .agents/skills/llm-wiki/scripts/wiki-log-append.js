// =============================================================================
// LLM-Wiki Log Append (Stop Hook)
// 스킬 실행 종료 시 log.md에 연산 기록을 append하는 후처리 스크립트
// IMP-002: Node.js 우선 사용
// IMP-005: WIKI_ROOT = ../001_Wiki_AI
// =============================================================================

const fs = require('fs');
const path = require('path');

const WIKI_ROOT = path.resolve(process.cwd(), '../001_Wiki_AI');
const LOG_PATH = path.join(WIKI_ROOT, 'log.md');

// Stop hook receives tool output via stdin
let data = '';
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  try {
    // Update the "updated" date in log.md frontmatter
    if (!fs.existsSync(LOG_PATH)) {
      process.exit(0);
    }

    let logContent = fs.readFileSync(LOG_PATH, { encoding: 'utf-8' });

    // Update frontmatter date
    const today = new Date().toISOString().slice(0, 10);
    logContent = logContent.replace(
      /^(updated:\s*")[\d-]+(")$/m,
      '$1' + today + '$2'
    );

    // Count entries
    const entryCount = (logContent.match(/^\| \d{6}/gm) || []).length;
    logContent = logContent.replace(
      /^(total_entries:\s*)\d+$/m,
      '$1' + entryCount
    );

    fs.writeFileSync(LOG_PATH, logContent, { encoding: 'utf-8' });
  } catch (e) {
    // Silent failure - hooks should not block
  }
});
