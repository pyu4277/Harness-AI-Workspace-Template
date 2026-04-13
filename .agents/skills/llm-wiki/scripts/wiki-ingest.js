#!/usr/bin/env node
// =============================================================================
// wiki-ingest.js -- ingest 시 관련 페이지 10-15개 후보 추출 + patch JSON 제안
// Reference-Port 출처: Karpathy LLM Wiki Gist "ingest lifecycle" 아이디어
//   (코드 복사 없음 — 우리 3축 분류에 맞춰 자체 구현)
//
// 입력: argv[2] = ingest 대상 파일 경로 (.md 또는 .txt)
// 출력: stdout JSON {
//   target: "path",
//   summary: "...",
//   related: [{path, score, reason}, ...],  // 10-15개
//   patch_suggestions: [{file, action, diff}, ...]
// }
// 규칙:
//   - 실제 파일을 수정하지 않는다 (dry-run). 호출자 승인 후 적용.
//   - 연관도 = 토큰 교집합 점수 (간단 Jaccard + 도메인 prefix 가중).
// =============================================================================

const fs = require('fs');
const path = require('path');

const WIKI_ROOT = process.env.WIKI_ROOT
  ? path.resolve(process.env.WIKI_ROOT)
  : path.resolve(process.cwd(), '..', '001_Wiki_AI');
const TARGET_MIN = 10;
const TARGET_MAX = 15;

function tokenize(text) {
  // 한/영 혼합 단순 토크나이즈: 2자 이상 단어만 채택
  const tokens = text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .split(/\s+/)
    .filter(t => t.length >= 2);
  return new Set(tokens);
}

function jaccard(a, b) {
  if (a.size === 0 || b.size === 0) return 0;
  let inter = 0;
  for (const x of a) if (b.has(x)) inter++;
  return inter / (a.size + b.size - inter);
}

function walkMd(dir) {
  const out = [];
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
  catch { return out; }
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (e.name === '000_Raw' || e.name === 'Clippings' ||
          e.name === 'archive' || e.name.startsWith('.')) continue;
      out.push(...walkMd(full));
    } else if (e.isFile() && e.name.endsWith('.md')) {
      out.push(full);
    }
  }
  return out;
}

function summarize(text) {
  const stripped = text.replace(/^---[\s\S]*?---\n/, '').replace(/\s+/g, ' ').trim();
  return stripped.slice(0, 200) + (stripped.length > 200 ? ' ...' : '');
}

function domainOf(relPath) {
  const parts = relPath.split(/[\\/]/);
  return parts[0] || '';
}

function main() {
  const targetArg = process.argv[2];
  if (!targetArg) {
    console.error('Usage: node wiki-ingest.js <target-file-path>');
    process.exit(1);
  }
  const target = path.resolve(targetArg);
  if (!fs.existsSync(target)) {
    console.error('ERROR: target not found: ' + target);
    process.exit(1);
  }
  const targetText = fs.readFileSync(target, 'utf-8');
  const targetTokens = tokenize(targetText);
  const targetDomain = domainOf(path.relative(WIKI_ROOT, target).replace(/\\/g, '/'));

  const pages = walkMd(WIKI_ROOT);
  const scored = [];
  for (const p of pages) {
    if (path.resolve(p) === target) continue;
    let txt;
    try { txt = fs.readFileSync(p, 'utf-8'); } catch { continue; }
    const toks = tokenize(txt);
    let score = jaccard(targetTokens, toks);
    const rel = path.relative(WIKI_ROOT, p).replace(/\\/g, '/');
    // 도메인 일치 가중 10%
    if (targetDomain && rel.startsWith(targetDomain + '/')) score += 0.1;
    if (score > 0) {
      const reason = rel.startsWith(targetDomain + '/')
        ? 'same-domain token-overlap'
        : 'token-overlap';
      scored.push({ path: rel, score: Number(score.toFixed(4)), reason });
    }
  }

  scored.sort((a, b) => b.score - a.score);
  const related = scored.slice(0, TARGET_MAX);
  if (related.length < TARGET_MIN) {
    // 후보 부족 — 최대치만 반환, 경고 메시지 포함
    process.stderr.write('[wiki-ingest] WARN: 후보 ' + related.length + '개 < 최소 ' + TARGET_MIN + '개\n');
  }

  const patches = related.map(r => ({
    file: r.path,
    action: 'append-related-link',
    diff: '- 관련: [' + path.basename(target, '.md') + '](' +
      path.relative(path.dirname(path.join(WIKI_ROOT, r.path)),
        target).replace(/\\/g, '/') + ')'
  }));

  const report = {
    target: path.relative(WIKI_ROOT, target).replace(/\\/g, '/'),
    summary: summarize(targetText),
    token_count: targetTokens.size,
    related,
    patch_suggestions: patches,
    stats: {
      total_pages_scanned: pages.length,
      candidates_found: scored.length,
      target_min: TARGET_MIN,
      target_max: TARGET_MAX,
    },
    generated: new Date().toISOString(),
  };

  console.log(JSON.stringify(report, null, 2));
}

if (require.main === module) main();
module.exports = { tokenize, jaccard };
