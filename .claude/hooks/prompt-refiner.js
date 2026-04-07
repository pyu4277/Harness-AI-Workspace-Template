// =============================================================================
// Harness: UserPromptSubmit - Imprint Auto-Recall
// 각인 키워드 매칭 + recall_count 자동 증가 (각인 전용)
// 용어 정제/ToT 판단은 CLAUDE.md 행동 규칙으로 처리 (AI가 의미 이해 가능)
// =============================================================================

const fs = require('fs');
const path = require('path');

const IMPRINTS_PATH = path.join(process.cwd(), '.harness', 'imprints.json');

let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const hookData = JSON.parse(input);
    const userMessage = hookData.message || '';

    if (!userMessage || userMessage.length < 3) {
      process.exit(0);
    }

    if (!fs.existsSync(IMPRINTS_PATH)) {
      process.exit(0);
    }

    const data = JSON.parse(fs.readFileSync(IMPRINTS_PATH, 'utf8'));
    const imprints = data.imprints || [];
    const msgLower = userMessage.toLowerCase();
    const matched = [];

    for (const imp of imprints) {
      const keywords = imp.trigger_keywords || [];
      const hits = keywords.filter(kw => msgLower.includes(kw.toLowerCase()));
      if (hits.length > 0) {
        matched.push({ imp, hits, hitCount: hits.length });
      }
    }

    if (matched.length === 0) {
      process.exit(0);
    }

    // 매칭 수 기준 정렬, 상위 3개
    matched.sort((a, b) => b.hitCount - a.hitCount);
    const top = matched.slice(0, 3);

    // recall_count 증가 + last_recalled 갱신
    const now = new Date().toISOString();
    for (const m of top) {
      const idx = imprints.findIndex(i => i.id === m.imp.id);
      if (idx !== -1) {
        imprints[idx].recall_count = (imprints[idx].recall_count || 0) + 1;
        imprints[idx].last_recalled = now;
      }
    }
    data.stats.total_recalls = (data.stats.total_recalls || 0) + top.length;
    data.stats.last_updated = now;
    fs.writeFileSync(IMPRINTS_PATH, JSON.stringify(data, null, 2), 'utf8');

    // stderr로 각인 알림
    for (const m of top) {
      process.stderr.write(
        `[각인 ${m.imp.id}] ${m.imp.principle} (매칭: ${m.hits.join(', ')})\n`
      );
    }

  } catch (e) {
    // 실패 시 조용히 통과
  }
});
