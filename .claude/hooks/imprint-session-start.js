// =============================================================================
// Harness Imprint: SessionStart - Active Imprints Generator
// Pillar 4 (Feedback Loop): 세션 시작 시 상위 각인을 active-imprints.md로 자동 갱신
// 추가: decay 로직 + 12개 초과 시 최하위 제거 + 원자적 쓰기
// =============================================================================

const fs = require('fs');
const path = require('path');

const IMPRINTS_PATH = path.join(process.cwd(), '.harness', 'imprints.json');
const ARCHIVE_PATH = path.join(process.cwd(), '.harness', 'imprints-archive.json');
const ACTIVE_PATH = path.join(process.cwd(), '.harness', 'active-imprints.md');
const DECAY_LOG_PATH = path.join(process.cwd(), '.harness', 'imprint-decay.log');

const MAX_ACTIVE = 10;      // active-imprints.md에 표시할 상위 개수
const MAX_IMPRINTS = 12;    // imprints.json 최대 보관 개수
const DECAY_DAYS = 30;      // decay 기준: 30일 미리콜 + recall_count=0

// --- 원자적 쓰기 헬퍼 ---
function atomicWrite(filePath, content) {
  const tmp = filePath + '.tmp.' + Date.now();
  fs.writeFileSync(tmp, content, 'utf8');
  fs.renameSync(tmp, filePath);
}

// --- 가중치 계산 ---
const SEVERITY_SCORE = { critical: 4, high: 3, medium: 2, low: 1 };

function calcWeight(imp, now) {
  const sev = SEVERITY_SCORE[imp.severity] || 1;
  const recalls = imp.recall_count || 0;
  const ageDays = (now - new Date(imp.created).getTime()) / (1000 * 60 * 60 * 24);
  const freshness = Math.max(0, 1 - ageDays / 365);
  return sev * (1 + recalls) + freshness * 2;
}

// --- decay 판정 ---
function isDecayable(imp, now) {
  const recalls = imp.recall_count || 0;
  if (recalls > 0) return false;
  const ageMs = now - new Date(imp.created).getTime();
  const ageDays = ageMs / (1000 * 60 * 60 * 24);
  return ageDays > DECAY_DAYS;
}

// --- 아카이브 추가 ---
function appendToArchive(decayed) {
  if (decayed.length === 0) return;
  let archive = { version: '1.0', imprints: [] };
  if (fs.existsSync(ARCHIVE_PATH)) {
    try {
      archive = JSON.parse(fs.readFileSync(ARCHIVE_PATH, 'utf8'));
      if (!archive.imprints) archive.imprints = [];
    } catch (e) {
      // 파싱 실패 시 새로 시작
      archive = { version: '1.0', imprints: [] };
    }
  }
  const archivedAt = new Date().toISOString();
  for (const imp of decayed) {
    archive.imprints.push({ ...imp, archived_at: archivedAt });
  }
  atomicWrite(ARCHIVE_PATH, JSON.stringify(archive, null, 2));
}

// --- decay 로그 ---
function logDecay(decayed, reason) {
  if (decayed.length === 0) return;
  const timestamp = new Date().toISOString();
  const lines = decayed.map(imp =>
    `${timestamp} | ${reason} | ${imp.id} | ${imp.severity} | ${imp.principle.slice(0, 80)}`
  );
  try {
    fs.appendFileSync(DECAY_LOG_PATH, lines.join('\n') + '\n', 'utf8');
  } catch (e) {
    // 로그 실패는 무시
  }
}

// --- 메인 로직 ---
try {
  if (!fs.existsSync(IMPRINTS_PATH)) {
    process.exit(0);
  }

  const data = JSON.parse(fs.readFileSync(IMPRINTS_PATH, 'utf8'));
  let imprints = data.imprints || [];

  if (imprints.length === 0) {
    process.exit(0);
  }

  const now = Date.now();
  let mutated = false;

  // --- 1단계: decay 체크 (30일 미리콜 + recall_count=0) ---
  const decayedByAge = imprints.filter(imp => isDecayable(imp, now));
  if (decayedByAge.length > 0) {
    const decayedIds = new Set(decayedByAge.map(i => i.id));
    imprints = imprints.filter(imp => !decayedIds.has(imp.id));
    appendToArchive(decayedByAge);
    logDecay(decayedByAge, 'age-decay');
    mutated = true;
    process.stderr.write(
      '[각인] decay: ' + decayedByAge.length + '개 각인 아카이브 (30일 미리콜)\n'
    );
  }

  // --- 2단계: 12개 초과 시 최하위 weight 제거 ---
  if (imprints.length > MAX_IMPRINTS) {
    const weighted = imprints.map(imp => ({ imp, w: calcWeight(imp, now) }));
    weighted.sort((a, b) => a.w - b.w); // 오름차순 (최하위 먼저)
    const excess = weighted.slice(0, imprints.length - MAX_IMPRINTS).map(x => x.imp);
    const excessIds = new Set(excess.map(i => i.id));
    imprints = imprints.filter(imp => !excessIds.has(imp.id));
    appendToArchive(excess);
    logDecay(excess, 'over-limit');
    mutated = true;
    process.stderr.write(
      '[각인] 한계 초과: ' + excess.length + '개 최하위 각인 아카이브 (12개 제한)\n'
    );
  }

  // --- 3단계: imprints.json 갱신 (원자적) ---
  if (mutated) {
    const updated = {
      version: data.version || '1.0',
      imprints: imprints,
      stats: {
        total_imprints: imprints.length,
        total_recalls: imprints.reduce((sum, i) => sum + (i.recall_count || 0), 0),
        last_updated: new Date().toISOString()
      }
    };
    atomicWrite(IMPRINTS_PATH, JSON.stringify(updated, null, 2));
  }

  // --- 4단계: active-imprints.md 생성 (상위 10개) ---
  const scored = imprints.map(imp => ({ ...imp, score: calcWeight(imp, now) }));
  scored.sort((a, b) => b.score - a.score);
  const top = scored.slice(0, MAX_ACTIVE);

  const lines = [
    '# Active Imprints (자동 생성 -- 직접 편집 금지)',
    '',
    '> 가장 최근 + 가장 자주 회수된 각인. 세션 시작 시 imprint-session-start.js가 자동 갱신.',
    '> 각인 = 기록보다 상위. 유사 상황 발생 시 자동으로 떠오르는 구조적 기억.',
    '',
    '| ID | 심각도 | 원칙 | 트리거 키워드 |',
    '|---|---|---|---|'
  ];

  for (const imp of top) {
    const keywords = (imp.trigger_keywords || []).slice(0, 3).join(', ');
    lines.push(`| ${imp.id} | ${imp.severity} | ${imp.principle} | ${keywords} |`);
  }

  lines.push('');
  lines.push(`> 총 ${imprints.length}개 각인 중 상위 ${top.length}개 표시. 전체 목록: /imprint list`);
  if (mutated) {
    lines.push(`> 이번 세션에서 ${decayedByAge.length} + ${Math.max(0, imprints.length > MAX_IMPRINTS ? imprints.length - MAX_IMPRINTS : 0)} 개 각인이 아카이브로 이동됨. 상세: \`.harness/imprint-decay.log\``);
  }

  atomicWrite(ACTIVE_PATH, lines.join('\n'));

} catch (e) {
  // 실패 시 조용히 통과 (세션 시작을 막으면 안 됨)
  process.stderr.write('[각인] imprint-session-start 오류: ' + e.message + '\n');
}
