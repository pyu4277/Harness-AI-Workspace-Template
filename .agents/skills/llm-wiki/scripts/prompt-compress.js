#!/usr/bin/env node
// =============================================================================
// prompt-compress.js -- NL 프롬프트 → 전문용어 압축 엔진
// Reference-Port 출처: MindVault README "CJK 토크나이저" 아이디어만 차용
//   (우리 재구현 범위: Intl.Segmenter + 정규식 기반 독자 구현, 코드 복사 없음)
// =============================================================================
//
// 입력: stdin JSON {"message": "...원문..."}
// 출력: stdout JSON {"compressed": "...압축본...", "hits": [{from,to}], "score": N}
// 규칙: 원문 파괴 금지 — 압축본을 제안만, 실제 치환은 호출자 결정
//
// 연결:
//   - prompt-refiner.js (UserPromptSubmit 훅)에서 호출
//   - 용어사전 경로: docs/LogManagement/용어사전.md (CLAUDE.md L56 기준)
//   - 로그 경로: .harness/refine-log.jsonl
// =============================================================================

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.cwd();
const GLOSSARY_PATH = path.join(PROJECT_ROOT, 'docs', 'LogManagement', '용어사전.md');
const REFINE_LOG = path.join(PROJECT_ROOT, '.harness', 'refine-log.jsonl');
const PROMOTE_MD = path.join(
  PROJECT_ROOT, '..', '001_Wiki_AI', '990_Meta', 'promote-candidates.md'
);
const PROMOTE_THRESHOLD = 30;

// 용어사전 파싱: | 전문용어 | 장황한 자연어 원문 | ...
function loadGlossary() {
  if (!fs.existsSync(GLOSSARY_PATH)) return [];
  const text = fs.readFileSync(GLOSSARY_PATH, 'utf8');
  const rows = text.match(/^\|[^\n]+\|[^\n]+\|[^\n]*$/gm) || [];
  const entries = [];
  for (const row of rows) {
    const cells = row.split('|').map(c => c.trim()).filter(c => c);
    if (cells.length < 2) continue;
    const term = cells[0];
    const original = cells[1];
    if (!term || !original || term === original) continue;
    if (term === '전문용어' || original === '원문') continue; // 헤더 제외
    if (original.length < 4) continue; // 너무 짧은 원문은 과매칭 방지
    entries.push({ term, original });
  }
  return entries;
}

// CJK 허용 토크나이즈 — Intl.Segmenter 사용 (Node 16+)
function tokenize(text) {
  try {
    const seg = new Intl.Segmenter('ko', { granularity: 'word' });
    return [...seg.segment(text)].map(s => s.segment);
  } catch {
    return text.split(/(\s+)/);
  }
}

// Levenshtein 거리 (작은 입력 전용)
function lev(a, b) {
  const m = a.length, n = b.length;
  if (m === 0) return n;
  if (n === 0) return m;
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost);
    }
  }
  return dp[m][n];
}

// 원문에서 압축 후보 검색 — 정확 포함 우선, Levenshtein 근사 2순위
function findMatches(message, entries) {
  const hits = [];
  for (const e of entries) {
    if (message.includes(e.original)) {
      hits.push({ from: e.original, to: e.term, mode: 'exact' });
      continue;
    }
    // 근사 매칭: 원문 길이 ±20% 윈도우 슬라이딩
    const L = e.original.length;
    const tol = Math.max(2, Math.floor(L * 0.2));
    const step = Math.max(1, Math.floor(L / 4));
    for (let i = 0; i <= message.length - L + tol; i += step) {
      const window = message.slice(i, i + L);
      if (window.length < L - tol) break;
      const d = lev(window, e.original);
      if (d <= tol) {
        hits.push({ from: window, to: e.term, mode: 'fuzzy', dist: d });
        break;
      }
    }
  }
  return hits;
}

function applyCompression(message, hits) {
  let out = message;
  // exact 먼저 적용 — 긴 원문부터 (중복 치환 방지)
  const sorted = [...hits].sort((a, b) => b.from.length - a.from.length);
  for (const h of sorted) {
    if (h.mode === 'exact') {
      out = out.split(h.from).join(h.to);
    }
  }
  return out;
}

function appendLog(entry) {
  try {
    fs.mkdirSync(path.dirname(REFINE_LOG), { recursive: true });
    fs.appendFileSync(REFINE_LOG, JSON.stringify(entry) + '\n', 'utf8');
  } catch {
    // 실패 조용히 통과 — 훅이 프롬프트 흐름 막지 않음
  }
}

function countLogLines() {
  if (!fs.existsSync(REFINE_LOG)) return 0;
  try {
    const text = fs.readFileSync(REFINE_LOG, 'utf8');
    return text.split('\n').filter(l => l.trim()).length;
  } catch {
    return 0;
  }
}

function promoteIfThreshold() {
  const count = countLogLines();
  if (count < PROMOTE_THRESHOLD) return null;
  if (count % PROMOTE_THRESHOLD !== 0) return null;
  try {
    const lines = fs.readFileSync(REFINE_LOG, 'utf8').split('\n').filter(l => l.trim());
    const recent = lines.slice(-PROMOTE_THRESHOLD).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
    // 빈도 집계
    const freq = new Map();
    for (const r of recent) {
      for (const h of (r.hits || [])) {
        const key = h.to;
        freq.set(key, (freq.get(key) || 0) + 1);
      }
    }
    const top = [...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10);
    const ts = new Date().toISOString();
    const body = [
      '# 프롬프트 압축 승격 후보 (auto-generated)',
      '',
      `- 생성 시각: ${ts}`,
      `- 로그 총 ${count}건 중 최근 ${PROMOTE_THRESHOLD}건 분석`,
      '',
      '| 전문용어 | 빈도 |',
      '|----------|------|',
      ...top.map(([t, f]) => `| ${t} | ${f} |`),
    ].join('\n');
    fs.mkdirSync(path.dirname(PROMOTE_MD), { recursive: true });
    fs.writeFileSync(PROMOTE_MD, body, 'utf8');
    return PROMOTE_MD;
  } catch {
    return null;
  }
}

function main() {
  let input = '';
  process.stdin.on('data', c => input += c);
  process.stdin.on('end', () => {
    let message = '';
    try {
      const data = JSON.parse(input);
      message = data.message || '';
    } catch {
      // raw text fallback
      message = input;
    }
    if (!message || message.length < 4) {
      process.stdout.write(JSON.stringify({ compressed: message, hits: [], score: 0 }));
      return;
    }
    const entries = loadGlossary();
    const hits = findMatches(message, entries);
    const compressed = applyCompression(message, hits);
    const score = hits.length;
    if (score > 0) {
      appendLog({
        ts: new Date().toISOString(),
        original_len: message.length,
        compressed_len: compressed.length,
        hits: hits.map(h => ({ from: h.from, to: h.to, mode: h.mode })),
      });
      const promoted = promoteIfThreshold();
      process.stdout.write(JSON.stringify({ compressed, hits, score, promoted }));
    } else {
      process.stdout.write(JSON.stringify({ compressed: message, hits: [], score: 0 }));
    }
  });
}

if (require.main === module) main();

module.exports = { loadGlossary, findMatches, applyCompression, tokenize };
