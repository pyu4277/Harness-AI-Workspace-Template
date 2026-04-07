// =============================================================================
// Harness Guard: PreToolUse - Write/Edit Path Guard
// Pillar 3 (Tool Boundaries): 허용된 경로에만 쓰기 허용
// =============================================================================

let data = '';
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  try {
    const j = JSON.parse(data);
    const filePath = (j.tool_input || {}).file_path || '';
    if (!filePath) { process.exit(0); }

    // 경로 정규화: 슬래시 통일 + 소문자
    const norm = p => p.replace(/\\/g, '/').toLowerCase();
    const normFile = norm(filePath);
    const normCwd = norm(process.cwd());

    // 상대경로 추출
    let rel = normFile;
    if (rel.startsWith(normCwd + '/')) {
      rel = rel.slice(normCwd.length + 1);
    }

    // --- 차단 경로 (명시적 deny) ---
    const blocked = [
      '.claude/settings.json',
      '.claude/settings.local.json',
      '.claude/hooks.json',
      '.env',
      'node_modules/',
      '.git/'
    ];

    for (const b of blocked) {
      if (rel === b || rel.startsWith(b)) {
        console.log(JSON.stringify({
          decision: 'block',
          reason: '하네스 가드: 보호된 설정 파일 쓰기 차단 - ' + b
        }));
        process.exit(0);
      }
    }

    // --- 허용 경로 (명시적 allow) ---
    const allowed = [
      /^src\//, /^docs\//, /^projects\//,
      /^\.agents\/skills\//, /^\.agents\/agents\//, /^\.agents\/templates\//,
      /^output\//, /^temporary storage\//, /^log\//, /^input\//,
      /^claude\.md$/, /^code-convention\.md$/, /^adr\.md$/,
      /^\.gitignore$/, /^requirements\.txt$/, /^bkit\.config\.json$/
    ];

    const isAllowed = allowed.some(rx => rx.test(rel));
    if (!isAllowed) {
      console.log(JSON.stringify({
        decision: 'block',
        reason: '하네스 가드: 허용 경로 외 쓰기 차단 - ' + rel +
          '. 허용: src/, docs/, Projects/, .agents/, Output/, Temporary Storage/'
      }));
    }
    // 허용 시 조용히 통과 (성공은 조용히, 실패만 시끄럽게)
  } catch (e) {
    // 파싱 실패 시 통과
  }
});
