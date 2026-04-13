// =============================================================================
// Obsidian CLI Detect (IMP-006: Hybrid Mode Detection)
// Obsidian 실행 상태 + CLI 가용성을 감지하여 mode를 결정한다.
// IMP-002: Node.js 우선 사용 (Windows PATH 보장)
// =============================================================================

const { execSync } = require('child_process');

function checkObsidianRunning() {
  try {
    const result = execSync('tasklist /FI "IMAGENAME eq Obsidian.exe" /NH', {
      encoding: 'utf-8',
      timeout: 5000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return result.toLowerCase().includes('obsidian.exe');
  } catch (e) {
    return false;
  }
}

function checkCliAvailable() {
  try {
    const result = execSync('obsidian version', {
      encoding: 'utf-8',
      timeout: 5000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return result.trim().length > 0;
  } catch (e) {
    return false;
  }
}

function checkVaultAccessible(vaultName) {
  try {
    const result = execSync('obsidian vault vault="' + vaultName + '"', {
      encoding: 'utf-8',
      timeout: 5000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return result.trim().length > 0;
  } catch (e) {
    return false;
  }
}

// Phase 3 확장: vault 수집 시 기존 `[[wikilinks]]`·frontmatter·`#tags` 보존 여부 검증 + 통계
function scanVaultPreservation(vaultRoot) {
  const fs = require('fs');
  const path = require('path');
  if (!fs.existsSync(vaultRoot)) {
    return { scanned: 0, wikilinks: 0, frontmatter_pages: 0, tag_usages: 0,
      warning: 'vault root not found' };
  }
  let scanned = 0, wikilinks = 0, fmPages = 0, tagUsages = 0;
  function walk(dir) {
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) {
        if (e.name.startsWith('.') || e.name === 'archive') continue;
        walk(full);
      } else if (e.isFile() && e.name.endsWith('.md')) {
        scanned++;
        let txt;
        try { txt = fs.readFileSync(full, 'utf-8'); } catch { continue; }
        wikilinks += (txt.match(/\[\[[^\]]+\]\]/g) || []).length;
        if (/^---\n[\s\S]*?\n---/.test(txt)) fmPages++;
        tagUsages += (txt.match(/(^|\s)#[A-Za-z가-힣0-9_][\w가-힣_-]*/g) || []).length;
      }
    }
  }
  walk(vaultRoot);
  return { scanned, wikilinks, frontmatter_pages: fmPages, tag_usages: tagUsages };
}

function main() {
  const path = require('path');
  const vaultName = process.argv[2] || '001_Wiki_AI';
  const vaultRoot = process.env.WIKI_ROOT
    ? path.resolve(process.env.WIKI_ROOT)
    : path.resolve(process.cwd(), '..', vaultName);

  const obsidianRunning = checkObsidianRunning();
  const cliAvailable = obsidianRunning ? checkCliAvailable() : false;
  const vaultAccessible = cliAvailable ? checkVaultAccessible(vaultName) : false;

  const mode = (obsidianRunning && cliAvailable) ? 'cli' : 'filesystem';
  const preservation = scanVaultPreservation(vaultRoot);

  const report = {
    obsidian_running: obsidianRunning,
    cli_available: cliAvailable,
    vault_accessible: vaultAccessible,
    vault_name: vaultName,
    vault_root: vaultRoot,
    mode: mode,
    preservation: preservation,
    timestamp: new Date().toISOString()
  };

  console.log(JSON.stringify(report));

  // Human-readable summary to stderr
  if (mode === 'cli') {
    console.error('Obsidian CLI: ACTIVE (vault: ' + vaultName + ')');
  } else {
    console.error('Obsidian CLI: INACTIVE -> filesystem fallback');
    if (!obsidianRunning) {
      console.error('  Reason: Obsidian is not running');
    } else if (!cliAvailable) {
      console.error('  Reason: CLI command not found in PATH');
    }
  }
}

main();
