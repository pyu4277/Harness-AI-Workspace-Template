// =============================================================================
// Navigator Auto-Updater: PostToolUse - Write/Edit
// SYSTEM_NAVIGATOR.md 자동 갱신 훅
// Phase 6: AUTO 마커 기반 실제 내용 교체 (6 reader 호출)
// =============================================================================

const fs = require('fs');
const path = require('path');
const helpers = require('./navigator-updater-helpers.js');

let data = '';
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  try {
    const j = JSON.parse(data);
    const filePath = (j.tool_input || {}).file_path || '';
    if (!filePath) { process.exit(0); }

    const norm = p => p.replace(/\\/g, '/').toLowerCase();
    const normFile = norm(filePath);
    const normCwd = norm(process.cwd());

    let rel = normFile;
    if (rel.startsWith(normCwd + '/')) {
      rel = rel.slice(normCwd.length + 1);
    }

    // --- 감시 파일 -> 섹션 마커 매핑 ---
    const watchMap = [
      { pattern: /^\.agents\/skills\/.*\/skill\.md$/, marker: 'skills-catalog', label: '스킬 카탈로그' },
      { pattern: /^\.mcp\.json$/, marker: 'mcp-servers', label: 'MCP 서버' },
      { pattern: /^\.claude\/commands\/.*\.md$/, marker: 'commands', label: '커맨드' },
      { pattern: /^\.harness\/imprints\.json$/, marker: 'imprints', label: '각인 시스템' },
      { pattern: /^\.claude\/hooks\/pre-tool-guard\.js$/, marker: 'pre-tool-guard', label: '경로 가드' },
      { pattern: /^\.bkit\/plugin\/scripts\//, marker: 'bkit-scripts', label: 'bkit 스크립트' }
    ];

    const matched = watchMap.find(w => w.pattern.test(rel));
    if (!matched) { process.exit(0); }

    const navPath = path.join(process.cwd(), 'SYSTEM_NAVIGATOR.md');
    if (!fs.existsSync(navPath)) {
      process.stderr.write('[네비게이터] SYSTEM_NAVIGATOR.md 파일 없음 - 갱신 건너뜀\n');
      process.exit(0);
    }

    process.stderr.write(
      '[네비게이터] 갱신 감지: ' + matched.label +
      ' (변경: ' + rel + ')\n'
    );

    // --- Reader 매핑 ---
    const readerMap = {
      'skills-catalog': () => helpers.readSkillsCatalog(process.cwd()),
      'mcp-servers': () => helpers.readMcpServers(process.cwd()),
      'commands': () => helpers.readCommands(process.cwd()),
      'imprints': () => helpers.readImprints(process.cwd()),
      'pre-tool-guard': () => helpers.readPreToolGuard(process.cwd()),
      'bkit-scripts': () => helpers.readBkitScripts(process.cwd())
    };

    const reader = readerMap[matched.marker];
    if (!reader) {
      process.stderr.write('[네비게이터] reader 없음: ' + matched.marker + '\n');
      helpers.appendHistory(navPath, matched.label, rel, 'no-reader');
      process.exit(0);
    }

    // --- Reader 실행 ---
    let newContent;
    try {
      newContent = reader();
      if (!newContent) throw new Error('reader returned null');
    } catch (e) {
      process.stderr.write('[네비게이터] reader 실패: ' + matched.marker + ' - ' + e.message + '\n');
      helpers.appendHistory(navPath, matched.label, rel, 'reader-failed');
      process.exit(0);
    }

    // --- 교체 + 원자적 쓰기 ---
    try {
      const current = fs.readFileSync(navPath, 'utf8');
      const currentSize = current.length;
      const updated = helpers.replaceAutoSection(current, matched.marker, newContent);

      // 안전 검증: 파일 크기 50% 이하로 감소 시 중단
      if (updated.length < currentSize * 0.5) {
        throw new Error('교체 후 파일 크기 50% 이하로 감소 (' + currentSize + ' -> ' + updated.length + ')');
      }

      helpers.atomicWriteWithBackup(navPath, updated);
      helpers.appendHistory(navPath, matched.label, rel, 'success');
      process.stderr.write('[네비게이터] ' + matched.label + ' 섹션 자동 갱신 완료\n');
    } catch (e) {
      process.stderr.write('[네비게이터] 교체 실패: ' + e.message + '\n');
      helpers.appendHistory(navPath, matched.label, rel, 'replace-failed');
    }

  } catch (e) {
    // 파싱 실패 시 조용히 통과
  }
});
