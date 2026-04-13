// =============================================================================
// Harness Imprint: SessionStart - Wiki Clippings Detection
// Pillar 4 (Feedback Loop): IMP-036
// 미처리 Clippings 누적 감지 -- 침묵 누적 차단
// =============================================================================

const fs = require('fs');
const path = require('path');

const WIKI_ROOT = path.resolve(process.cwd(), '..', '001_Wiki_AI');
const CLIPPINGS_DIR = path.join(WIKI_ROOT, 'Clippings');
const ARCHIVE_DIR = path.join(WIKI_ROOT, '990_Meta', 'archive');
const SOURCES_DIR = path.join(WIKI_ROOT, '500_Technology', 'sources');

const ROOT_CLIPPING_PATTERN = /^\d{4}-\d{2}-\d{2} VIDEO /;
const MAX_AGE_HOURS = 24;

function listDirSafe(dir) {
  try { return fs.readdirSync(dir); } catch { return []; }
}

function fileAgeHours(filePath) {
  try {
    const mtime = fs.statSync(filePath).mtimeMs;
    return (Date.now() - mtime) / (1000 * 60 * 60);
  } catch { return 0; }
}

function checkClippingsFolder() {
  const files = listDirSafe(CLIPPINGS_DIR).filter(f => f.endsWith('.md'));
  return files.map(f => {
    const fp = path.join(CLIPPINGS_DIR, f);
    return { file: f, ageHours: fileAgeHours(fp), location: 'Clippings/' };
  });
}

function checkRootClippings() {
  const files = listDirSafe(WIKI_ROOT)
    .filter(f => f.endsWith('.md') && ROOT_CLIPPING_PATTERN.test(f));
  return files.map(f => {
    const fp = path.join(WIKI_ROOT, f);
    return { file: f, ageHours: fileAgeHours(fp), location: 'root/' };
  });
}

function main() {
  if (!fs.existsSync(WIKI_ROOT)) return;

  const pending = [...checkClippingsFolder(), ...checkRootClippings()];
  if (pending.length === 0) return;

  const stale = pending.filter(p => p.ageHours >= MAX_AGE_HOURS);
  const fresh = pending.filter(p => p.ageHours < MAX_AGE_HOURS);

  const lines = [];
  lines.push('[Wiki] 미처리 Clippings ' + pending.length + '건 감지 (IMP-036)');
  if (stale.length > 0) {
    lines.push('  STALE (' + MAX_AGE_HOURS + 'h 이상): ' + stale.length + '건 -- 즉시 처리 권장');
    stale.slice(0, 5).forEach(p => {
      lines.push('    - [' + p.location + '] ' + p.file + ' (' + Math.round(p.ageHours) + 'h)');
    });
  }
  if (fresh.length > 0) {
    lines.push('  FRESH (24h 이내): ' + fresh.length + '건');
  }
  lines.push('  처리: /llm-wiki ingest 또는 수동 Level B 발췌 후 990_Meta/archive/ 이동 (IMP-023)');

  process.stderr.write(lines.join('\n') + '\n');
}

try { main(); } catch (e) {
  process.stderr.write('[wiki-clippings-check] ' + e.message + '\n');
}
