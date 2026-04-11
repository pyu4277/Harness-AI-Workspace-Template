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
    // multi: true 면 단일 트리거가 여러 마커를 동시 갱신
    const watchMap = [
      { pattern: /^\.agents\/skills\/.*\/skill\.md$/, markers: ['skills-catalog'], labels: ['스킬 카탈로그'] },
      { pattern: /^\.mcp\.json$/, markers: ['mcp-servers'], labels: ['MCP 서버'] },
      { pattern: /^\.claude\/commands\/.*\.md$/, markers: ['commands'], labels: ['커맨드'] },
      { pattern: /^\.harness\/imprints\.json$/, markers: ['imprints'], labels: ['각인 시스템'] },
      { pattern: /^\.claude\/hooks\/pre-tool-guard\.js$/, markers: ['pre-tool-guard'], labels: ['경로 가드'] },
      { pattern: /^\.bkit\/plugin\/scripts\//, markers: ['bkit-scripts'], labels: ['bkit 스크립트'] },
      // Option C: Navigator.md 변경 시 4개 마커 동시 갱신
      // 단, SYSTEM_NAVIGATOR.md 자체 변경은 제외 (무한 루프 방지)
      { pattern: /^\.agents\/skills\/.*_navigator\.md$/, markers: ['navigators-meta', 'pattern-stats', 'gap-analysis', 'navigator-diagram'], labels: ['Navigator 카탈로그', '패턴 통계', 'Gap 분석', 'Navigator 다이어그램'] }
    ];

    const matched = watchMap.find(w => w.pattern.test(rel));
    if (!matched) { process.exit(0); }

    const navPath = path.join(process.cwd(), 'SYSTEM_NAVIGATOR.md');
    if (!fs.existsSync(navPath)) {
      process.stderr.write('[네비게이터] SYSTEM_NAVIGATOR.md 파일 없음 - 갱신 건너뜀\n');
      process.exit(0);
    }

    process.stderr.write(
      '[네비게이터] 갱신 감지: ' + matched.labels.join(', ') +
      ' (변경: ' + rel + ')\n'
    );

    // --- Reader 매핑 ---
    const readerMap = {
      'skills-catalog':    () => helpers.readSkillsCatalog(process.cwd()),
      'mcp-servers':       () => helpers.readMcpServers(process.cwd()),
      'commands':          () => helpers.readCommands(process.cwd()),
      'imprints':          () => helpers.readImprints(process.cwd()),
      'pre-tool-guard':    () => helpers.readPreToolGuard(process.cwd()),
      'bkit-scripts':      () => helpers.readBkitScripts(process.cwd()),
      // Option C: Navigator 자동 집계 readers
      'navigators-meta':   () => helpers.readNavigatorsMeta(process.cwd()),
      'pattern-stats':     () => helpers.readPatternStats(process.cwd()),
      'gap-analysis':      () => helpers.readGapAnalysis(process.cwd()),
      'navigator-diagram': () => helpers.readNavigatorDiagram(process.cwd())
    };

    // --- 마커별 순차 처리 (한 트리거가 여러 마커 갱신 가능) ---
    let current;
    try {
      current = fs.readFileSync(navPath, 'utf8');
    } catch (e) {
      process.stderr.write('[네비게이터] SYSTEM_NAVIGATOR.md 읽기 실패: ' + e.message + '\n');
      process.exit(0);
    }
    const originalSize = current.length;

    let updateCount = 0;
    let failCount = 0;

    for (let i = 0; i < matched.markers.length; i++) {
      const markerId = matched.markers[i];
      const label = matched.labels[i];
      const reader = readerMap[markerId];

      if (!reader) {
        process.stderr.write('[네비게이터] reader 없음: ' + markerId + '\n');
        helpers.appendHistory(navPath, label, rel, 'no-reader');
        failCount++;
        continue;
      }

      // Reader 실행
      let newContent;
      try {
        newContent = reader();
        if (newContent == null) throw new Error('reader returned null');
      } catch (e) {
        process.stderr.write('[네비게이터] reader 실패: ' + markerId + ' - ' + e.message + '\n');
        failCount++;
        continue;
      }

      // 마커 영역 교체 (마커 없으면 스킵, 다음 마커로)
      try {
        const replaced = helpers.replaceAutoSection(current, markerId, newContent);
        current = replaced;
        updateCount++;
      } catch (e) {
        // 마커가 SYSTEM_NAVIGATOR.md에 없는 경우 (선택적 갱신, 에러 아님)
        process.stderr.write('[네비게이터] 마커 미존재 (스킵): ' + markerId + '\n');
        continue;
      }
    }

    // --- 원자적 쓰기 ---
    if (updateCount > 0) {
      try {
        // 안전 검증: 파일 크기 50% 이하로 감소 시 중단
        if (current.length < originalSize * 0.5) {
          throw new Error('교체 후 파일 크기 50% 이하로 감소 (' + originalSize + ' -> ' + current.length + ')');
        }
        helpers.atomicWriteWithBackup(navPath, current);
        helpers.appendHistory(navPath, matched.labels.join('+'), rel, updateCount + '/' + matched.markers.length + ' updated');
        process.stderr.write('[네비게이터] ' + updateCount + '개 섹션 자동 갱신 완료\n');
      } catch (e) {
        process.stderr.write('[네비게이터] 쓰기 실패: ' + e.message + '\n');
        helpers.appendHistory(navPath, matched.labels.join('+'), rel, 'write-failed');
      }
    } else {
      process.stderr.write('[네비게이터] 갱신할 마커 없음 (모두 미존재)\n');
    }

  } catch (e) {
    // 파싱 실패 시 조용히 통과
  }
});
