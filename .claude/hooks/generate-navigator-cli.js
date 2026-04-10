// =============================================================================
// Navigator Scaffold CLI Entry Point
// Usage: node .claude/hooks/generate-navigator-cli.js <skillName> [--dry-run] [--out=PATH]
// =============================================================================

const fs = require('fs');
const path = require('path');
const helpers = require('./navigator-updater-helpers.js');

function printUsage() {
  process.stderr.write('Usage: node .claude/hooks/generate-navigator-cli.js <skillName> [--dry-run] [--out=PATH]\n');
  process.stderr.write('\n');
  process.stderr.write('Options:\n');
  process.stderr.write('  <skillName>    스킬 디렉토리 이름 (예: HWPX_Master)\n');
  process.stderr.write('  --dry-run      파일 쓰지 않고 stdout에만 출력\n');
  process.stderr.write('  --out=PATH     출력 경로 지정 (기본: .agents/skills/<skillName>/<skillName>_Navigator.md)\n');
}

function parseArgs(argv) {
  const args = { skillName: null, dryRun: false, outPath: null };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--dry-run') args.dryRun = true;
    else if (a.startsWith('--out=')) args.outPath = a.slice(6);
    else if (a === '-h' || a === '--help') { printUsage(); process.exit(0); }
    else if (!args.skillName) args.skillName = a;
  }
  return args;
}

function main() {
  const args = parseArgs(process.argv);
  if (!args.skillName) {
    printUsage();
    process.exit(1);
  }

  const cwd = process.cwd();

  let markdown;
  try {
    markdown = helpers.generateNavigatorScaffold(cwd, args.skillName, {
      preserveExisting: true,
      appendHistoryRow: true
    });
  } catch (e) {
    process.stderr.write('[FAIL] scaffold 생성 실패: ' + e.message + '\n');
    process.exit(2);
  }

  // 크기 안전 체크
  if (!markdown || markdown.length < 500) {
    process.stderr.write('[FAIL] 생성된 markdown이 너무 작음 (' + (markdown ? markdown.length : 0) + ' bytes)\n');
    process.exit(3);
  }

  if (args.dryRun) {
    process.stdout.write(markdown);
    process.stderr.write('\n[OK] dry-run 완료 (' + markdown.length + ' bytes)\n');
    process.exit(0);
  }

  const defaultOut = path.join(cwd, '.agents', 'skills', args.skillName, args.skillName + '_Navigator.md');
  const outPath = args.outPath ? path.resolve(cwd, args.outPath) : defaultOut;

  try {
    // 기존 파일 있으면 .bak 백업 (atomicWriteWithBackup이 자동 수행)
    helpers.atomicWriteWithBackup(outPath, markdown);
    process.stderr.write('[OK] Navigator scaffold 생성 완료\n');
    process.stderr.write('      경로: ' + outPath + '\n');
    process.stderr.write('      크기: ' + markdown.length + ' bytes\n');
    process.stderr.write('      라인: ' + markdown.split('\n').length + '\n');
    if (fs.existsSync(outPath + '.bak')) {
      process.stderr.write('      백업: ' + outPath + '.bak\n');
    }
  } catch (e) {
    process.stderr.write('[FAIL] 파일 쓰기 실패: ' + e.message + '\n');
    process.exit(4);
  }
}

main();
