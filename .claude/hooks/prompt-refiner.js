// =============================================================================
// Harness: UserPromptSubmit - Prompt Refiner + Term Matcher
// 용어사전 매칭으로 프롬프트 품질 자동 향상 + 각인 자동 회수 통합
// =============================================================================

const fs = require('fs');
const path = require('path');

const GLOSSARY_PATH = path.join(process.cwd(), 'docs', 'LogManagement', '용어사전.md');
const IMPRINTS_PATH = path.join(process.cwd(), '.harness', 'imprints.json');

// --- 용어사전 파싱 ---
function parseGlossary(content) {
  const terms = [];
  const lines = content.split('\n');
  let inTable = false;

  for (const line of lines) {
    if (line.startsWith('| 번호 |') || line.startsWith('| :--:')) {
      inTable = true;
      continue;
    }
    if (!inTable || !line.startsWith('|')) continue;

    const cols = line.split('|').map(c => c.trim()).filter(c => c);
    if (cols.length >= 6) {
      const term = cols[1];       // 한국어 용어
      const original = cols[2];   // 원어
      const easyDesc = cols[5];   // 쉬운 설명
      if (term && original && !term.match(/^번호$/)) {
        terms.push({ term, original, easyDesc });
      }
    }
  }
  return terms;
}

// --- 고정 용어 교정 맵 ---
const FIXED_CORRECTIONS = [
  { pattern: /요약/gi, replacement: '발췌 정리', note: '"요약"은 환각 위험. 원문에서 핵심을 발췌하여 정리' },
  { pattern: /대충/gi, replacement: '개략적으로', note: '비공식 표현을 전문 표현으로 교정' },
  { pattern: /간단하게/gi, replacement: '핵심만 간결하게', note: '모호한 지시를 구체화' },
];

let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const hookData = JSON.parse(input);
    const userMessage = hookData.message || '';

    if (!userMessage || userMessage.length < 5) {
      process.exit(0);
    }

    const context = [];

    // --- 1. 고정 교정 매칭 ---
    for (const fix of FIXED_CORRECTIONS) {
      if (fix.pattern.test(userMessage)) {
        context.push(`[프롬프트 정제] "${fix.pattern.source}" -> "${fix.replacement}" (${fix.note})`);
      }
    }

    // --- 2. 용어사전 매칭 ---
    if (fs.existsSync(GLOSSARY_PATH)) {
      const glossaryContent = fs.readFileSync(GLOSSARY_PATH, 'utf8');
      const terms = parseGlossary(glossaryContent);
      const msgLower = userMessage.toLowerCase();
      const matched = [];

      for (const t of terms) {
        // 용어 한국어명 또는 원어가 메시지에 포함되는지 확인
        const termLower = t.term.toLowerCase();
        const origLower = t.original.toLowerCase();
        const origWords = origLower.split(/[\s\/()]+/).filter(w => w.length > 2);

        if (msgLower.includes(termLower) || origWords.some(w => msgLower.includes(w))) {
          matched.push(t);
        }
      }

      if (matched.length > 0) {
        const termList = matched.slice(0, 5).map(t =>
          `  - ${t.term}(${t.original}): ${t.easyDesc.substring(0, 60)}`
        ).join('\n');
        context.push(`[용어사전 매칭] 관련 전문용어 감지:\n${termList}`);
      }
    }

    // --- 3. 각인(Imprint) 매칭 ---
    if (fs.existsSync(IMPRINTS_PATH)) {
      const data = JSON.parse(fs.readFileSync(IMPRINTS_PATH, 'utf8'));
      const imprints = data.imprints || [];
      const msgLower = userMessage.toLowerCase();
      const impMatched = [];

      for (const imp of imprints) {
        const keywords = imp.trigger_keywords || [];
        const hits = keywords.filter(kw => msgLower.includes(kw.toLowerCase()));
        if (hits.length > 0) {
          impMatched.push({ imp, hits });
        }
      }

      if (impMatched.length > 0) {
        // recall_count 증가
        const now = new Date().toISOString();
        for (const m of impMatched) {
          const idx = imprints.findIndex(i => i.id === m.imp.id);
          if (idx !== -1) {
            imprints[idx].recall_count = (imprints[idx].recall_count || 0) + 1;
            imprints[idx].last_recalled = now;
          }
        }
        data.stats.total_recalls = (data.stats.total_recalls || 0) + impMatched.length;
        data.stats.last_updated = now;
        fs.writeFileSync(IMPRINTS_PATH, JSON.stringify(data, null, 2), 'utf8');

        for (const m of impMatched.slice(0, 3)) {
          context.push(`[각인 ${m.imp.id}] ${m.imp.principle} (매칭: ${m.hits.join(', ')})`);
        }
      }
    }

    // --- 출력 ---
    if (context.length > 0) {
      // stderr로 컨텍스트 주입 (에이전트가 인지하되 사용자 메시지는 변경하지 않음)
      process.stderr.write(context.join('\n') + '\n');
    }

  } catch (e) {
    // 실패 시 조용히 통과
  }
});
