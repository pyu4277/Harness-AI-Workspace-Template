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

function main() {
  const vaultName = process.argv[2] || '001_Wiki_AI';

  const obsidianRunning = checkObsidianRunning();
  const cliAvailable = obsidianRunning ? checkCliAvailable() : false;
  const vaultAccessible = cliAvailable ? checkVaultAccessible(vaultName) : false;

  const mode = (obsidianRunning && cliAvailable) ? 'cli' : 'filesystem';

  const report = {
    obsidian_running: obsidianRunning,
    cli_available: cliAvailable,
    vault_accessible: vaultAccessible,
    vault_name: vaultName,
    mode: mode,
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
