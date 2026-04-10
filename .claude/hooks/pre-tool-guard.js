// =============================================================================
// Harness Guard: PreToolUse - Write/Edit Path Guard
// Pillar 3 (Tool Boundaries): 허용된 경로에만 쓰기 허용
// =============================================================================

const fs = require('fs');

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
      /^\.harness\//,
      /^\.claude\/commands\//, /^\.claude\/hooks\//,
      /^output\//, /^temporary storage\//, /^log\//, /^input\//,
      /^claude\.md$/, /^code-convention\.md$/, /^adr\.md$/,
      /^\.gitignore$/, /^requirements\.txt$/, /^bkit\.config\.json$/,
      /^skills-lock\.json$/,
      /^system_navigator\.md$/,
      /^readme\.md$/,
      /^\.mcp\.json$/
    ];

    const isAllowed = allowed.some(rx => rx.test(rel));

    // --- 위키 형제 디렉토리 허용 (IMP-005: WIKI_ROOT = ../001_Wiki_AI) ---
    const parentDir = normCwd.replace(/\/[^/]+$/, '');
    const wikiRootLower = parentDir + '/001_wiki_ai';
    const isWikiPathCandidate = normFile.startsWith(wikiRootLower + '/');

    // WIKI_ROOT 실존 검증: 대소문자 양쪽 시도
    let isWikiPath = false;
    if (isWikiPathCandidate) {
      try {
        // fs는 Windows에서 대소문자 구분 없음. 원본 경로 기반 검증
        const parentDirRaw = process.cwd().replace(/[\\/][^\\/]+$/, '');
        const wikiRootRaw = parentDirRaw + '/001_Wiki_AI';
        isWikiPath = fs.existsSync(wikiRootRaw) || fs.existsSync(parentDirRaw + '/001_wiki_ai');
      } catch (e) {
        isWikiPath = false;
      }
    }

    if (!isAllowed && !isWikiPath) {
      // 위키 경로 후보였으나 실존 검증 실패한 경우 별도 메시지
      if (isWikiPathCandidate && !isWikiPath) {
        console.log(JSON.stringify({
          decision: 'block',
          reason: '하네스 가드: WIKI_ROOT(../001_Wiki_AI) 디렉토리가 존재하지 않아 쓰기 차단 - ' + rel +
            '. 위키 디렉토리 존재 확인 필요 (IMP-005).'
        }));
      } else {
        console.log(JSON.stringify({
          decision: 'block',
          reason: '하네스 가드: 허용 경로 외 쓰기 차단 - ' + rel +
            '. 허용: src/, docs/, Projects/, .agents/, .harness/, .claude/commands/, .claude/hooks/, Output/, Temporary Storage/, ../001_Wiki_AI/, skills-lock.json, system_navigator.md, .mcp.json'
        }));
      }
    }
    // 허용 시 조용히 통과 (성공은 조용히, 실패만 시끄럽게)
  } catch (e) {
    // 파싱 실패 시 통과
  }
});
