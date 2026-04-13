// =============================================================================
// LLM-Wiki Log Append (Stop Hook + lifecycle event recorder)
// - 원래 기능: Stop 훅에서 log.md frontmatter 갱신
// - Phase 1 확장: CLI 호출 시 lifecycle 이벤트를 log.md 표에 append
// IMP-002: Node.js 우선 사용
// IMP-005: WIKI_ROOT = ../001_Wiki_AI
// =============================================================================

const fs = require('fs');
const path = require('path');

const WIKI_ROOT = process.env.WIKI_ROOT
  ? path.resolve(process.env.WIKI_ROOT)
  : path.resolve(process.cwd(), '..', '001_Wiki_AI');
const LOG_PATH = path.join(WIKI_ROOT, 'log.md');

function yymmdd() {
  const d = new Date();
  const y = String(d.getFullYear()).slice(2);
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return y + m + day;
}

function refreshFrontmatter() {
  if (!fs.existsSync(LOG_PATH)) return;
  let logContent = fs.readFileSync(LOG_PATH, { encoding: 'utf-8' });
  const today = new Date().toISOString().slice(0, 10);
  logContent = logContent.replace(
    /^(updated:\s*")[\d-]+(")$/m,
    '$1' + today + '$2'
  );
  const entryCount = (logContent.match(/^\| \d{6}/gm) || []).length;
  logContent = logContent.replace(
    /^(total_entries:\s*)\d+$/m,
    '$1' + entryCount
  );
  fs.writeFileSync(LOG_PATH, logContent, { encoding: 'utf-8' });
}

// CLI: node wiki-log-append.js event <kind> <target> [note]
function appendLifecycleEvent(kind, target, note) {
  if (!fs.existsSync(LOG_PATH)) {
    process.stderr.write('[wiki-log-append] log.md not found: ' + LOG_PATH + '\n');
    process.exit(1);
  }
  let content = fs.readFileSync(LOG_PATH, { encoding: 'utf-8' });
  const row = '| ' + yymmdd() + ' | ' + kind + ' | ' + target + ' | ' + (note || '') + ' |';
  // append to end, ensure newline
  if (!content.endsWith('\n')) content += '\n';
  content += row + '\n';
  fs.writeFileSync(LOG_PATH, content, { encoding: 'utf-8' });
  refreshFrontmatter();
  process.stderr.write('[wiki-log-append] appended: ' + row + '\n');
}

// CLI 모드 감지: 첫 번째 인자가 'event' 면 lifecycle append
const argv = process.argv.slice(2);
if (argv[0] === 'event') {
  const [, kind, target, ...rest] = argv;
  if (!kind || !target) {
    console.error('Usage: node wiki-log-append.js event <kind> <target> [note]');
    process.exit(1);
  }
  appendLifecycleEvent(kind, target, rest.join(' '));
} else {
  // Stop hook receives tool output via stdin
  let data = '';
  process.stdin.on('data', chunk => data += chunk);
  process.stdin.on('end', () => {
    try { refreshFrontmatter(); } catch { /* silent */ }
  });
}

module.exports = { appendLifecycleEvent, refreshFrontmatter };
