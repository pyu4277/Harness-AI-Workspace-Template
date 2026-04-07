// =============================================================================
// Harness Imprint: UserPromptSubmit - Keyword Matcher
// Pillar 4 (Feedback Loop): 사용자 입력에서 각인 키워드를 매칭하여 자동 회수
// =============================================================================

const fs = require('fs');
const path = require('path');

const IMPRINTS_PATH = path.join(process.cwd(), '.harness', 'imprints.json');

let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    if (!fs.existsSync(IMPRINTS_PATH)) {
      process.exit(0);
    }

    const hookData = JSON.parse(input);
    const userMessage = (hookData.message || '').toLowerCase();

    if (!userMessage || userMessage.length < 3) {
      process.exit(0);
    }

    const data = JSON.parse(fs.readFileSync(IMPRINTS_PATH, 'utf8'));
    const imprints = data.imprints || [];
    const matched = [];

    for (const imp of imprints) {
      const keywords = imp.trigger_keywords || [];
      const hits = keywords.filter(kw => userMessage.includes(kw.toLowerCase()));

      if (hits.length > 0) {
        matched.push({ imp, hits, hitCount: hits.length });
      }
    }

    if (matched.length === 0) {
      process.exit(0);
    }

    // 매칭 수 기준 정렬, 상위 3개만
    matched.sort((a, b) => b.hitCount - a.hitCount);
    const top = matched.slice(0, 3);

    // recall_count 증가 + last_recalled 갱신
    const now = new Date().toISOString();
    let updated = false;

    for (const m of top) {
      const idx = imprints.findIndex(i => i.id === m.imp.id);
      if (idx !== -1) {
        imprints[idx].recall_count = (imprints[idx].recall_count || 0) + 1;
        imprints[idx].last_recalled = now;
        updated = true;
      }
    }

    if (updated) {
      data.stats.total_recalls = (data.stats.total_recalls || 0) + top.length;
      data.stats.last_updated = now;
      fs.writeFileSync(IMPRINTS_PATH, JSON.stringify(data, null, 2), 'utf8');
    }

    // stderr로 각인 알림 출력 (에이전트 컨텍스트에 주입)
    for (const m of top) {
      process.stderr.write(
        `[각인 ${m.imp.id}] ${m.imp.principle} (매칭: ${m.hits.join(', ')})\n`
      );
    }

  } catch (e) {
    // 실패 시 조용히 통과
  }
});
