// =============================================================================
// LLM-Wiki Lint Script (Node.js)
// IMP-002: Windows에서 node 우선 사용
// IMP-005: WIKI_ROOT = ../001_Wiki_AI (상대경로)
// IMP-006: Obsidian CLI Hybrid - CLI 가용 시 orphans/deadends/unresolved 활용
// =============================================================================

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WIKI_ROOT = process.argv[2] || path.resolve(process.cwd(), '../001_Wiki_AI');
const VAULT_NAME = process.argv[3] || '001_Wiki_AI';
const USE_CLI = process.argv.includes('--cli');

const REQUIRED_SUBFOLDERS = ['entities', 'concepts', 'sources', 'analysis'];
const DOMAIN_PATTERN = /^\d{3}_/;
const SOURCE_NAME_PATTERN = /^\d{6}_.*_V\d{3}\.md$/;
const REQUIRED_FRONTMATTER = ['title', 'domain', 'type', 'created', 'updated'];
const CURRENT_SCHEMA_VERSION = 2;

const issues = [];

function addIssue(severity, check, file, message, autoFixable) {
  issues.push({ severity, check, file, message, autoFixable: autoFixable || false });
}

// --- Check 1: Domain folder structure ---
function checkStructure() {
  if (!fs.existsSync(WIKI_ROOT)) {
    addIssue('CRITICAL', 'STRUCTURE', WIKI_ROOT, 'WIKI_ROOT does not exist');
    return;
  }

  const entries = fs.readdirSync(WIKI_ROOT, { withFileTypes: true });
  const domains = entries.filter(e => e.isDirectory() && DOMAIN_PATTERN.test(e.name) && e.name !== '000_Raw');

  for (const domain of domains) {
    const domainPath = path.join(WIKI_ROOT, domain.name);
    for (const sub of REQUIRED_SUBFOLDERS) {
      const subPath = path.join(domainPath, sub);
      if (!fs.existsSync(subPath)) {
        addIssue('WARNING', 'STRUCTURE', path.relative(WIKI_ROOT, subPath), 'Missing required subfolder', true);
      }
    }
  }
}

// --- Check 2: Orphan pages (not in index.md) ---
function checkOrphans() {
  const indexPath = path.join(WIKI_ROOT, 'index.md');
  if (!fs.existsSync(indexPath)) {
    addIssue('CRITICAL', 'ORPHAN', 'index.md', 'index.md does not exist');
    return;
  }

  const indexContent = fs.readFileSync(indexPath, { encoding: 'utf-8' });
  const allPages = getAllWikiPages();

  for (const page of allPages) {
    const relPath = path.relative(WIKI_ROOT, page).replace(/\\/g, '/');
    if (!indexContent.includes(relPath)) {
      addIssue('WARNING', 'ORPHAN', relPath, 'Page not registered in index.md', true);
    }
  }
}

// --- Check 3: Broken links ---
function checkBrokenLinks() {
  const allPages = getAllWikiPages();

  for (const pagePath of allPages) {
    let content;
    try {
      content = fs.readFileSync(pagePath, { encoding: 'utf-8' });
    } catch (e) {
      continue;
    }

    const linkPattern = /\[([^\]]*)\]\(([^)]+\.md)\)/g;
    let match;
    while ((match = linkPattern.exec(content)) !== null) {
      const linkTarget = match[2];
      if (linkTarget.startsWith('http')) continue;

      const resolvedPath = path.resolve(path.dirname(pagePath), linkTarget);
      if (!fs.existsSync(resolvedPath)) {
        const relPage = path.relative(WIKI_ROOT, pagePath).replace(/\\/g, '/');
        addIssue('WARNING', 'BROKEN_LINK', relPage, 'Broken link: ' + linkTarget, false);
      }
    }
  }
}

// --- Check 4: Naming convention ---
function checkNaming() {
  const allPages = getAllWikiPages();

  for (const pagePath of allPages) {
    const relPath = path.relative(WIKI_ROOT, pagePath).replace(/\\/g, '/');
    const parts = relPath.split('/');
    if (parts.length < 3) continue;

    const folder = parts[parts.length - 2];
    const fileName = parts[parts.length - 1];

    if ((folder === 'sources' || folder === 'analysis') && !SOURCE_NAME_PATTERN.test(fileName)) {
      addIssue('INFO', 'NAMING', relPath, 'File in ' + folder + '/ should follow YYMMDD_Subject_V001.md pattern');
    }

    if ((folder === 'entities' || folder === 'concepts') && /^\d{6}_/.test(fileName)) {
      addIssue('INFO', 'NAMING', relPath, 'File in ' + folder + '/ should NOT have date prefix (living document)');
    }
  }
}

// --- Check 5: Frontmatter ---
function checkFrontmatter() {
  const allPages = getAllWikiPages();

  for (const pagePath of allPages) {
    let content;
    try {
      content = fs.readFileSync(pagePath, { encoding: 'utf-8' });
    } catch (e) {
      continue;
    }

    const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (!fmMatch) {
      const relPath = path.relative(WIKI_ROOT, pagePath).replace(/\\/g, '/');
      addIssue('WARNING', 'FRONTMATTER', relPath, 'Missing YAML frontmatter', false);
      continue;
    }

    const fm = fmMatch[1];
    const relPath = path.relative(WIKI_ROOT, pagePath).replace(/\\/g, '/');

    for (const field of REQUIRED_FRONTMATTER) {
      if (!fm.includes(field + ':')) {
        addIssue('INFO', 'FRONTMATTER', relPath, 'Missing frontmatter field: ' + field, true);
      }
    }
  }
}

// --- Check 8: Shortcut bidirectional validation (v3.1) ---
function checkShortcuts() {
  const allPages = getAllWikiPages();

  for (const pagePath of allPages) {
    let content;
    try {
      content = fs.readFileSync(pagePath, { encoding: 'utf-8' });
    } catch (e) {
      continue;
    }

    const relPath = path.relative(WIKI_ROOT, pagePath).replace(/\\/g, '/');

    // A. Shortcut -> Canonical validation
    if (content.includes('type: shortcut')) {
      const canonicalMatch = content.match(/canonical:\s*"([^"]+)"/);
      if (!canonicalMatch) {
        addIssue('WARNING', 'SHORTCUT', relPath, 'Shortcut missing canonical path', false);
        continue;
      }
      const canonicalRel = canonicalMatch[1];
      const canonicalAbs = path.resolve(WIKI_ROOT, canonicalRel);
      if (!fs.existsSync(canonicalAbs)) {
        addIssue('WARNING', 'SHORTCUT_ORPHAN', relPath,
          'Shortcut points to non-existent canonical: ' + canonicalRel, false);
      }
    }

    // B. Canonical -> Shortcuts validation (정본의 shortcuts[] 검증)
    const shortcutsMatch = content.match(/shortcuts:\s*\n((?:\s*-\s*"[^"]+"\n?)*)/);
    if (shortcutsMatch) {
      const shortcuts = shortcutsMatch[1].match(/"([^"]+)"/g) || [];
      for (const raw of shortcuts) {
        const shortcutRel = raw.replace(/"/g, '');
        const shortcutAbs = path.resolve(WIKI_ROOT, shortcutRel);
        if (!fs.existsSync(shortcutAbs)) {
          addIssue('WARNING', 'CANONICAL_BROKEN_SHORTCUT', relPath,
            'Canonical lists non-existent shortcut: ' + shortcutRel, false);
        }
      }
    }
  }
}

// --- Check 9: Schema version diff (Phase 1) ---
// WIKI_ROOT/CLAUDE.md 의 schema_version: N 을 기준 버전으로 삼고,
// 각 페이지 프론트매터의 schema_version 값과 비교해 마이그레이션 대상을 감지한다.
function checkSchemaDiff() {
  const claudeMd = path.join(WIKI_ROOT, 'CLAUDE.md');
  let rootVer = CURRENT_SCHEMA_VERSION;
  if (fs.existsSync(claudeMd)) {
    try {
      const txt = fs.readFileSync(claudeMd, 'utf-8');
      const m = txt.match(/schema_version:\s*(\d+)/);
      if (m) rootVer = parseInt(m[1], 10);
    } catch (e) { /* fall through */ }
  }

  const allPages = getAllWikiPages();
  const migrationLog = [];
  for (const pagePath of allPages) {
    let content;
    try { content = fs.readFileSync(pagePath, 'utf-8'); } catch { continue; }
    const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (!fmMatch) continue;
    const fm = fmMatch[1];
    const verM = fm.match(/schema_version:\s*(\d+)/);
    const pageVer = verM ? parseInt(verM[1], 10) : 1;
    const relPath = path.relative(WIKI_ROOT, pagePath).replace(/\\/g, '/');
    if (pageVer < rootVer) {
      addIssue('INFO', 'SCHEMA_DIFF', relPath,
        'schema_version ' + pageVer + ' < root ' + rootVer + ' (migration candidate)', true);
      migrationLog.push({ file: relPath, from: pageVer, to: rootVer });
    }
  }

  if (migrationLog.length > 0) {
    try {
      const metaDir = path.join(WIKI_ROOT, '990_Meta');
      if (fs.existsSync(metaDir)) {
        const logFile = path.join(metaDir, 'schema-migration.log');
        const entry = '[' + new Date().toISOString() + '] root=' + rootVer +
          ' candidates=' + migrationLog.length + '\n' +
          migrationLog.map(m => '  ' + m.file + ' v' + m.from + ' -> v' + m.to).join('\n') + '\n';
        fs.appendFileSync(logFile, entry, 'utf-8');
      }
    } catch (e) { /* noop */ }
  }
}

// --- Helper: Get all wiki .md pages (excluding root files) ---
function getAllWikiPages() {
  const pages = [];

  function walk(dir) {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch (e) {
      return;
    }

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        // 제외: 000_Raw (미처리 큐), Clippings (미처리 큐), archive (원본 보관소, IMP-017), 숨김 폴더
        if (entry.name === '000_Raw' || entry.name === 'Clippings' || entry.name === 'archive' || entry.name.startsWith('.')) continue;
        walk(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        const relToRoot = path.relative(WIKI_ROOT, fullPath);
        if (!relToRoot.includes(path.sep) && !relToRoot.includes('/')) continue;
        pages.push(fullPath);
      }
    }
  }

  walk(WIKI_ROOT);
  return pages;
}

// --- Check 6: CLI-enhanced orphan detection (IMP-006) ---
function checkOrphansCli() {
  try {
    const result = execSync('obsidian orphans vault="' + VAULT_NAME + '"', {
      encoding: 'utf-8',
      timeout: 10000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    const lines = result.trim().split('\n').filter(l => l.trim());
    for (const line of lines) {
      addIssue('WARNING', 'ORPHAN_CLI', line.trim(), 'No incoming links (Obsidian CLI)', false);
    }
  } catch (e) {
    console.error('CLI orphans check failed, falling back to filesystem');
    checkOrphans();
  }
}

// --- Check 7: CLI-enhanced broken link detection (IMP-006) ---
function checkBrokenLinksCli() {
  try {
    // deadends: files with no outgoing links
    const deadends = execSync('obsidian deadends vault="' + VAULT_NAME + '"', {
      encoding: 'utf-8',
      timeout: 10000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    const deadLines = deadends.trim().split('\n').filter(l => l.trim());
    for (const line of deadLines) {
      addIssue('INFO', 'DEADEND_CLI', line.trim(), 'No outgoing links (dead end)', false);
    }

    // unresolved: links pointing to non-existent files
    const unresolved = execSync('obsidian unresolved vault="' + VAULT_NAME + '"', {
      encoding: 'utf-8',
      timeout: 10000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    const unresolvedLines = unresolved.trim().split('\n').filter(l => l.trim());
    for (const line of unresolvedLines) {
      addIssue('WARNING', 'UNRESOLVED_CLI', line.trim(), 'Unresolved link target', false);
    }
  } catch (e) {
    console.error('CLI link check failed, falling back to filesystem');
    checkBrokenLinks();
  }
}

// --- Main ---
function main() {
  console.error('Wiki Lint: ' + WIKI_ROOT + (USE_CLI ? ' [CLI mode]' : ' [filesystem mode]'));

  checkStructure();

  if (USE_CLI) {
    checkOrphansCli();
    checkBrokenLinksCli();
  } else {
    checkOrphans();
    checkBrokenLinks();
  }

  checkNaming();
  checkFrontmatter();
  checkShortcuts();
  checkSchemaDiff();

  // Output JSON to stdout
  const report = {
    wiki_root: WIKI_ROOT,
    timestamp: new Date().toISOString(),
    total_issues: issues.length,
    by_severity: {
      CRITICAL: issues.filter(i => i.severity === 'CRITICAL').length,
      WARNING: issues.filter(i => i.severity === 'WARNING').length,
      INFO: issues.filter(i => i.severity === 'INFO').length
    },
    issues: issues
  };

  console.log(JSON.stringify(report, null, 2));

  // Also output markdown summary to stderr for human reading
  if (issues.length === 0) {
    console.error('No issues found. Wiki is healthy.');
  } else {
    console.error('\n| Severity | Check | File | Issue | Auto-fix |');
    console.error('|:---|:---|:---|:---|:---:|');
    for (const i of issues) {
      console.error('| ' + i.severity + ' | ' + i.check + ' | ' + i.file + ' | ' + i.message + ' | ' + (i.autoFixable ? 'Y' : 'N') + ' |');
    }
  }
}

main();
