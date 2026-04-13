// =============================================================================
// wiki-extract-post.js -- PostToolUse hook
// 추출 스크립트 실행 후 graph.json 자동 갱신 (debounce: 60s 기준)
// 구조적 강제: 사용자가 명시적으로 graph-build 하지 않아도 그래프가 stale 되지 않음.
// =============================================================================

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const STAMP = path.join(process.cwd(), '.harness', 'last-graph-build.txt');
const DEBOUNCE_MS = 60 * 1000;

let input = '';
process.stdin.on('data', c => input += c);
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input || '{}');
    const toolName = (data.tool_name || '').toLowerCase();
    const args = JSON.stringify(data.tool_input || {});
    // 대상: wiki ingest 계열 스크립트 호출만
    const triggers = [
      'wiki-ingest', 'ast-extractor', 'leiden-cluster',
      'office-parse', 'pdf-cite', 'vision-caption'
    ];
    const isExtract = triggers.some(t => args.includes(t));
    if (!isExtract) return;

    // Debounce
    const now = Date.now();
    if (fs.existsSync(STAMP)) {
      const last = parseInt(fs.readFileSync(STAMP, 'utf-8').trim(), 10);
      if (!Number.isNaN(last) && now - last < DEBOUNCE_MS) {
        process.stderr.write('[wiki-extract-post] debounced\n');
        return;
      }
    }

    const script = path.join(process.cwd(), '.agents', 'skills', 'llm-wiki',
      'scripts', 'graph', 'graph-build.py');
    if (!fs.existsSync(script)) return;
    try {
      execSync('python "' + script + '"', { timeout: 30000, stdio: 'ignore' });
      fs.mkdirSync(path.dirname(STAMP), { recursive: true });
      fs.writeFileSync(STAMP, String(now), 'utf-8');
      process.stderr.write('[wiki-extract-post] graph.json refreshed\n');
    } catch (e) {
      process.stderr.write('[wiki-extract-post] graph-build failed (silent)\n');
    }
  } catch {
    // silent — harness 흐름 차단 금지
  }
});
