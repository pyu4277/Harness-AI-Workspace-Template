#!/usr/bin/env node
// PostToolUse(Write): CLAUDE.md와 settings.local.json 생성 시 4기둥 최소 요건 검증
// CLAUDE.md: 줄 수, 필수 섹션
// settings.local.json: deny 존재, 필수 차단 규칙

const fs = require('fs');

async function main() {
  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  try {
    const data = JSON.parse(input);

    if (data.tool_name !== 'Write') {
      process.stdout.write('{}');
      process.exit(0);
    }

    const filePath = data.tool_input?.file_path || '';

    // CLAUDE.md 검증
    if (filePath.endsWith('CLAUDE.md') && fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf-8');
      const lines = content.split('\n');
      const errors = [];

      // 500줄 초과 차단
      if (lines.length > 500) {
        errors.push(`CLAUDE.md가 ${lines.length}줄. 500줄 이하 필수 (권장 60줄)`);
      }

      // 필수 키워드 확인
      if (!content.match(/금지|prohibit|forbidden/i)) {
        errors.push('"절대 금지" 섹션이 없습니다. 하네스 기둥1 필수 요소');
      }

      // 프로젝트 설명 확인
      if (!content.match(/^# /m)) {
        errors.push('프로젝트 제목(# 헤딩)이 없습니다');
      }

      if (errors.length > 0) {
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: `4기둥 위반: ${errors.join('; ')}`
        }));
        process.exit(2);
      }
    }

    // settings.local.json 검증
    if (filePath.endsWith('settings.local.json') && fs.existsSync(filePath)) {
      try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const settings = JSON.parse(content);
        const errors = [];

        // permissions.deny 존재 확인
        if (!settings.permissions?.deny || settings.permissions.deny.length === 0) {
          errors.push('permissions.deny가 비어있습니다. 기둥3(도구 경계) 필수 요소');
        }

        // 필수 차단 규칙 확인
        const deny = (settings.permissions?.deny || []).join(' ');
        if (!deny.includes('rm -rf')) {
          errors.push('"rm -rf" 차단 규칙 필수');
        }
        if (!deny.includes('git push --force')) {
          errors.push('"git push --force" 차단 규칙 필수');
        }

        // hooks 존재 확인
        if (!settings.hooks || Object.keys(settings.hooks).length === 0) {
          errors.push('hooks 설정이 없습니다. 기둥2(CI/CD 게이트) 필수 요소');
        }

        if (errors.length > 0) {
          process.stdout.write(JSON.stringify({
            decision: 'block',
            reason: `4기둥 위반: ${errors.join('; ')}`
          }));
          process.exit(2);
        }
      } catch {
        // JSON 파싱 실패
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: 'settings.local.json 파싱 실패. 유효한 JSON인지 확인'
        }));
        process.exit(2);
      }
    }
  } catch {
    // 입력 파싱 실패
  }

  process.stdout.write('{}');
  process.exit(0);
}

main();
