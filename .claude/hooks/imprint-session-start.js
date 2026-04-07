// =============================================================================
// Harness Imprint: SessionStart - Active Imprints Generator
// Pillar 4 (Feedback Loop): 세션 시작 시 상위 각인을 active-imprints.md로 자동 갱신
// =============================================================================

const fs = require('fs');
const path = require('path');

const IMPRINTS_PATH = path.join(process.cwd(), '.harness', 'imprints.json');
const ACTIVE_PATH = path.join(process.cwd(), '.harness', 'active-imprints.md');
const MAX_ACTIVE = 10;

try {
  if (!fs.existsSync(IMPRINTS_PATH)) {
    process.exit(0);
  }

  const data = JSON.parse(fs.readFileSync(IMPRINTS_PATH, 'utf8'));
  const imprints = data.imprints || [];

  if (imprints.length === 0) {
    process.exit(0);
  }

  // 가중치 계산: severity 점수 * (1 + recall_count) + 최신순 보너스
  const severityScore = { critical: 4, high: 3, medium: 2, low: 1 };
  const now = Date.now();

  const scored = imprints.map(imp => {
    const sev = severityScore[imp.severity] || 1;
    const recalls = imp.recall_count || 0;
    const ageDays = (now - new Date(imp.created).getTime()) / (1000 * 60 * 60 * 24);
    const freshness = Math.max(0, 1 - ageDays / 365); // 1년 이내면 보너스
    const score = sev * (1 + recalls) + freshness * 2;
    return { ...imp, score };
  });

  // 상위 N개 선별
  scored.sort((a, b) => b.score - a.score);
  const top = scored.slice(0, MAX_ACTIVE);

  // active-imprints.md 생성
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

  fs.writeFileSync(ACTIVE_PATH, lines.join('\n'), 'utf8');

} catch (e) {
  // 실패 시 조용히 통과 (세션 시작을 막으면 안 됨)
}
