// =============================================================================
// Harness Guard: PostToolUse - Forbidden Pattern Detector
// Pillar 2 (CI/CD Gates): 금지 패턴을 구조적으로 차단
// =============================================================================

const fs = require('fs');

let data = '';
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  try {
    const j = JSON.parse(data);
    const filePath = (j.tool_input || {}).file_path || '';
    if (!filePath) { process.exit(0); }

    // 바이너리 파일 스킵
    const binExt = ['.hwpx', '.docx', '.pdf', '.pptx', '.xlsx', '.zip', '.gz',
      '.tar', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.woff', '.woff2', '.ttf', '.eot'];
    const ext = filePath.toLowerCase().slice(filePath.lastIndexOf('.'));
    if (binExt.includes(ext)) { process.exit(0); }

    // 파일 존재 확인
    if (!fs.existsSync(filePath)) { process.exit(0); }

    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const violations = [];

    // --- 검사 1: 이모티콘 (유니코드 범위) ---
    const emojiRanges = [
      [0x1F600, 0x1F64F], [0x1F300, 0x1F5FF], [0x1F680, 0x1F6FF],
      [0x1F1E0, 0x1F1FF], [0x2600, 0x26FF], [0x2700, 0x27BF],
      [0x1F900, 0x1F9FF], [0x1FA00, 0x1FA6F], [0x1FA70, 0x1FAFF]
    ];
    const emojiFound = [];
    for (let li = 0; li < lines.length && emojiFound.length < 3; li++) {
      for (const ch of lines[li]) {
        const cp = ch.codePointAt(0);
        for (const [s, e] of emojiRanges) {
          if (cp >= s && cp <= e) {
            emojiFound.push('line ' + (li + 1) + ': U+' + cp.toString(16).toUpperCase().padStart(4, '0'));
            break;
          }
        }
        if (emojiFound.length >= 3) break;
      }
    }
    if (emojiFound.length > 0) {
      violations.push('이모티콘 감지 (' + emojiFound.join('; ') + ')');
    }

    // --- 검사 2: 절대경로 하드코딩 ---
    const absRegex = /[A-Z]:\\|\/Users\/[a-zA-Z]|\/home\/[a-zA-Z]|C:\\Users\\/;
    for (let li = 0; li < lines.length; li++) {
      const line = lines[li];
      if (absRegex.test(line)) {
        // 주석/예시 제외
        if (/[#\/\/].*예|example|Example/i.test(line)) continue;
        violations.push('절대경로 하드코딩 (line ' + (li + 1) + ')');
        break;
      }
    }

    // --- 검사 3: 하드코딩된 시크릿 ---
    const secretRegex = /(api_key|api_secret|password|secret_key|access_token)\s*[:=]\s*['"][^'"]{8,}['"]/i;
    for (let li = 0; li < lines.length; li++) {
      if (secretRegex.test(lines[li])) {
        violations.push('하드코딩 시크릿 의심 (line ' + (li + 1) + ')');
        break;
      }
    }

    // --- 검사 4: 위험 함수 ---
    const dangerRegex = /eval\s*\(|new\s+Function\s*\(|document\.write\s*\(/;
    for (let li = 0; li < lines.length; li++) {
      if (dangerRegex.test(lines[li])) {
        violations.push('위험 함수 사용 (line ' + (li + 1) + ')');
        break;
      }
    }

    // --- 결과 ---
    if (violations.length > 0) {
      console.log(JSON.stringify({
        decision: 'block',
        reason: '하네스 가드: 금지 패턴 감지 - ' + violations.join('; ')
      }));
    }
    // 위반 없음 -> 조용히 통과
  } catch (e) {
    // 파싱 실패 시 통과
  }
});
