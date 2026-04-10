// =============================================================================
// Navigator Updater Helpers -- 6 Source Readers + Engine + Parser
// Phase 6: SYSTEM_NAVIGATOR.md 자동 갱신 엔진
// IMP-003: bash + node -e 이스케이프 지옥 회피 -- 별도 .js 파일
// =============================================================================

const fs = require('fs');
const path = require('path');

// --- Tier 매핑 (스킬명 → Tier/커맨드/요약) ---
const TIER_MAP = {
  'harness-architect':              { tier: 'S', command: '`/harness-architect init`', desc: '7단계 하네스 초기화 파이프라인' },
  'HWPX_Master':                    { tier: 'A', command: '자동 트리거', desc: '4-Track HWP/HWPX 문서 처리' },
  'llm-wiki':                       { tier: 'A', command: '대화형 호출', desc: '지식 관리 + 세션 핸드오프 통합 (3-mode Ingest)' },
  'PaperResearch':                  { tier: 'A', command: '자동 트리거', desc: '학술 논문 자동 검색' },
  'VisualCapture':                  { tier: 'A', command: '자동 트리거', desc: '3단계 시각 콘텐츠 파이프라인' },
  'auto-error-recovery':            { tier: 'B', command: '자동 트리거', desc: '4-phase 에러 복구 시스템' },
  'DocKit':                         { tier: 'B', command: '자동 트리거', desc: 'PDF/DOCX/PPTX 포맷 통합 처리' },
  'FileNameMaking':                 { tier: 'B', command: '자동 트리거', desc: '3단계 문서 평가 + 파일명 생성' },
  'harness-imprint':                { tier: 'B', command: '`/imprint [action]`', desc: '각인 기록/검색/통계/decay' },
  'mdGuide':                        { tier: 'B', command: '`/mdGuide [action]`', desc: 'Zero-Defect 마크다운 검증' },
  'Mermaid_FlowChart':              { tier: 'B', command: '자동 트리거', desc: 'ELK 렌더러 Mermaid 다이어그램 생성' },
  'PromptKit':                      { tier: 'B', command: '자동 트리거', desc: '5단계 프롬프트 변환/예시 생성' },
  'ServiceMaker':                   { tier: 'B', command: '자동 트리거', desc: '9단계 스킬 개발 표준 절차' },
  'term-organizer':                 { tier: 'B', command: '대화형 호출', desc: '전문용어 자동 추출/정리' },
  'pdca':                           { tier: 'C', command: '`/pdca [action]`', desc: 'PDCA 전체 주기 관리' },
  'btw':                            { tier: 'C', command: '`/btw [suggestion]`', desc: '개선 제안 수집/분석/승격' },
  'code-review':                    { tier: 'C', command: '`/code-review [target]`', desc: '코드 품질 분석' },
  'development-pipeline':           { tier: 'C', command: '`/development-pipeline`', desc: '9단계 개발 파이프라인 가이드' },
  'plan-plus':                      { tier: 'C', command: '`/plan-plus [feature]`', desc: '브레인스토밍 강화 기획' },
  'zero-script-qa':                 { tier: 'C', command: '`/zero-script-qa [target]`', desc: 'Docker 로그 기반 제로 스크립트 QA' },
  'bkit-rules':                     { tier: 'C', command: '자동 로드', desc: 'PDCA 규칙/레벨 감지' },
  'bkit-templates':                 { tier: 'C', command: '자동 로드', desc: 'PDCA 문서 템플릿' },
  'supabase':                       { tier: '외부', command: '자동 트리거', desc: 'Supabase 통합 (외부 스킬)' },
  'supabase-postgres-best-practices': { tier: '외부', command: '자동 트리거', desc: 'Supabase Postgres 최적화 (외부)' }
};

// --- SECTION_PATTERNS: Navigator 보존 섹션 헤더 정규식 (IMP-019 대응) ---
// 실측 기반: 6개 Navigator에서 관찰된 변형명 + SKILL.md 영문 헤더 커버
const SECTION_PATTERNS = {
  scenarios: /사용\s*시나리오|예시\s*시나리오|시나리오|사용\s*예시|Scenarios?|Examples?|Use\s*Cases?/i,
  constraints: /제약사항|제약|공통\s*주의사항|주의사항|주의점|금지\s*사항|절대\s*금지|안전\s*규칙|Constraints?|Notes?|Limitations?|Restrictions?|Safety/i
};

// --- MCP 용도 매핑 ---
const MCP_PURPOSE = {
  memory:                 '대화 간 메모리 저장/검색',
  'sequential-thinking':  '다단계 추론 (사고 흐름 구조화)',
  'token-optimizer':      '토큰 최적화',
  firecrawl:              '웹 크롤링/스크래핑',
  'fal-ai':               'AI 미디어 생성 (이미지/비디오)',
  'exa-web-search':       '시맨틱 웹 검색',
  jira:                   'Jira 이슈 관리',
  confluence:             'Confluence 문서 관리',
  supabase:               'Supabase DB 관리'
};

// --- 차단/허용 경로 설명 매핑 ---
const BLOCKED_DESC = {
  '.claude/settings.json':       '도구 권한 설정 보호',
  '.claude/settings.local.json': '환경 변수/보안 설정 보호',
  '.claude/hooks.json':          '훅 구성 보호',
  '.env':                        '환경 변수 보호',
  'node_modules/':               '의존성 보호',
  '.git/':                       'Git 내부 보호'
};

const ALLOWED_DESC = {
  'src/':                  '소스 코드',
  'docs/':                 '문서',
  'projects/':             '프로젝트 폴더',
  '.agents/skills/':       '스킬 정의',
  '.agents/agents/':       '에이전트 정의',
  '.agents/templates/':    '템플릿',
  '.harness/':             '각인 시스템',
  '.claude/commands/':     '슬래시 커맨드',
  '.claude/hooks/':        '하네스 훅 스크립트',
  'output/':               '출력물',
  'temporary storage/':    '임시 저장소',
  'log/':                  '로그',
  'input/':                '입력 파일',
  'claude.md':             '루트 거버넌스',
  'code-convention.md':    '코딩 규칙',
  'adr.md':                '아키텍처 결정',
  'system_navigator.md':   '시스템 네비게이터',
  '.gitignore':            'Git 제외 설정',
  'requirements.txt':      'Python 의존성',
  'bkit.config.json':      'bkit 설정',
  'skills-lock.json':      '스킬 무결성 잠금',
  'readme.md':             '프로젝트 README',
  '.mcp.json':             'MCP 서버 설정'
};

// --- bkit 카테고리 규칙 ---
const CATEGORY_RULES = [
  { cat: 'PDCA 코어',            match: /^(pdca-|phase-transition)/ },
  { cat: '파이프라인 (Phase 1~9)', match: /^phase\d/ },
  { cat: '코드 품질',             match: /^(code-analyzer|code-review)/ },
  { cat: '설계/검증',             match: /^(design-validator|gap-detector)/ },
  { cat: 'QA',                 match: /^qa-/ },
  { cat: '세션/팀',              match: /^(subagent|team|cto)/ },
  { cat: '통합 훅',              match: /^unified-/ },
  { cat: '유틸리티',              match: /^(pre-write|select-template|sync-folders|validate-plugin)/ },
  { cat: '세션 관리',            match: /^(context-compaction|post-compaction|user-prompt|stop-failure|skill-post)/ },
  { cat: '분석/보고',            match: /^(analysis-|archive-|iterator-|learning-)/ },
  { cat: '기타',                match: /.*/ }
];

// --- YAML 프론트매터 파서 (외부 의존성 없음) ---
function parseFrontmatter(content) {
  const m = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return {};
  const body = m[1];
  const fm = {};
  const lines = body.split(/\r?\n/);
  let currentKey = null;
  let multilineBuffer = [];
  let inMultiline = false;

  const flushMultiline = () => {
    if (inMultiline && currentKey) {
      fm[currentKey] = multilineBuffer.join('\n').trim();
      inMultiline = false;
      multilineBuffer = [];
    }
  };

  for (const line of lines) {
    if (inMultiline) {
      if (line.length === 0 || /^\s/.test(line)) {
        multilineBuffer.push(line.replace(/^\s{2}/, ''));
        continue;
      } else {
        flushMultiline();
      }
    }
    const kv = line.match(/^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$/);
    if (kv) {
      currentKey = kv[1];
      const value = kv[2].trim();
      if (value === '|' || value === '>') {
        inMultiline = true;
        multilineBuffer = [];
      } else if (value.startsWith('"') && value.endsWith('"')) {
        fm[currentKey] = value.slice(1, -1);
      } else if (value.startsWith("'") && value.endsWith("'")) {
        fm[currentKey] = value.slice(1, -1);
      } else {
        fm[currentKey] = value;
      }
    }
  }
  flushMultiline();
  return fm;
}

function firstLine(s) {
  if (!s) return '';
  const line = s.split(/\r?\n/)[0] || '';
  return line.trim();
}

function truncate(s, max) {
  if (!s) return '';
  if (s.length <= max) return s;
  return s.slice(0, max - 3) + '...';
}

function escapeMdCell(s) {
  if (!s) return '';
  return s.replace(/\|/g, '\\|');
}

// --- Reader 1: 스킬 카탈로그 ---
function readSkillsCatalog(cwd) {
  const skillsDir = path.join(cwd, '.agents', 'skills');
  if (!fs.existsSync(skillsDir)) return null;

  const entries = fs.readdirSync(skillsDir, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name)
    .sort();

  const rows = [];
  let idx = 1;
  for (const name of entries) {
    const skillPath = path.join(skillsDir, name, 'SKILL.md');
    if (!fs.existsSync(skillPath)) continue;

    let meta = TIER_MAP[name];
    if (!meta) {
      try {
        const content = fs.readFileSync(skillPath, 'utf8');
        const fm = parseFrontmatter(content);
        meta = {
          tier: 'B',
          command: fm['argument-hint'] ? '자동 트리거' : '자동 트리거',
          desc: truncate(firstLine(fm.description) || '(설명 없음)', 60)
        };
      } catch (e) {
        meta = { tier: 'B', command: '자동 트리거', desc: '(파싱 실패)' };
      }
    }

    rows.push(`| ${idx} | ${escapeMdCell(name)} | ${meta.tier} | ${escapeMdCell(meta.command)} | [작동] | ${escapeMdCell(meta.desc)} |`);
    idx++;
  }

  const header = [
    '',
    `### 커스텀 스킬 전체 목록 (${rows.length}개)`,
    '',
    '| # | 스킬명 | Tier | 커맨드 | 상태 | 요약 |',
    '|---|--------|------|--------|------|------|'
  ];
  return header.concat(rows).join('\n');
}

// --- Reader 2: MCP 서버 ---
function readMcpServers(cwd) {
  const mcpPath = path.join(cwd, '.mcp.json');
  if (!fs.existsSync(mcpPath)) return null;

  const raw = JSON.parse(fs.readFileSync(mcpPath, 'utf8'));
  const servers = raw.mcpServers || {};
  const names = Object.keys(servers);

  const rows = names.map((name, i) => {
    const cfg = servers[name];
    const type = cfg.type === 'http' ? 'http' : (cfg.command || 'unknown');
    const purpose = MCP_PURPOSE[name] || '(용도 미등록)';
    return `| ${i + 1} | ${escapeMdCell(name)} | ${type} | ${escapeMdCell(purpose)} | [작동] |`;
  });

  const header = [
    '',
    '| # | 서버 | 유형 | 용도 | 상태 |',
    '|---|------|------|------|------|'
  ];
  return header.concat(rows).join('\n');
}

// --- Reader 3: 슬래시 커맨드 ---
function readCommands(cwd) {
  const cmdDir = path.join(cwd, '.claude', 'commands');
  if (!fs.existsSync(cmdDir)) return null;

  const files = fs.readdirSync(cmdDir)
    .filter(f => f.endsWith('.md'))
    .sort();

  const rows = [];
  for (const f of files) {
    const full = path.join(cmdDir, f);
    const name = f.replace(/\.md$/, '');
    let fm = {};
    try {
      const content = fs.readFileSync(full, 'utf8');
      fm = parseFrontmatter(content);
    } catch (e) {
      continue;
    }
    const argHint = fm['argument-hint'] || '-';
    const desc = truncate(firstLine(fm.description) || '(설명 없음)', 80);
    rows.push(`| \`/${name}\` | \`${escapeMdCell(argHint)}\` | ${escapeMdCell(desc)} | ${name} |`);
  }

  const header = [
    '',
    '| 커맨드 | 인수 | 설명 | 스킬 |',
    '|--------|------|------|------|'
  ];
  return header.concat(rows).join('\n');
}

// --- Reader 4: 각인 시스템 ---
function readImprints(cwd) {
  const impPath = path.join(cwd, '.harness', 'imprints.json');
  if (!fs.existsSync(impPath)) return null;

  const data = JSON.parse(fs.readFileSync(impPath, 'utf8'));
  const imprints = data.imprints || [];

  const rows = imprints.map(imp => {
    const kw = (imp.trigger_keywords || []).slice(0, 3).join(', ');
    const principle = truncate(imp.principle || '', 80);
    return `| ${imp.id} | ${imp.severity || '-'} | ${escapeMdCell(principle)} | ${escapeMdCell(kw)} |`;
  });

  const header = [
    '',
    `**현재 활성 각인** (${imprints.length}개):`,
    '',
    '| ID | 심각도 | 원칙 | 트리거 키워드 |',
    '|----|--------|------|---------------|'
  ];
  return header.concat(rows).join('\n');
}

// --- Reader 5: pre-tool-guard 경로 ---
function readPreToolGuard(cwd) {
  const guardPath = path.join(cwd, '.claude', 'hooks', 'pre-tool-guard.js');
  if (!fs.existsSync(guardPath)) return null;

  const content = fs.readFileSync(guardPath, 'utf8');

  // blocked 추출
  const blockedMatch = content.match(/const\s+blocked\s*=\s*\[([\s\S]*?)\]/);
  if (!blockedMatch) throw new Error('blocked 배열 파싱 실패');
  const blockedStrs = [];
  const blockedRegex = /['"`]([^'"`]+)['"`]/g;
  let m;
  while ((m = blockedRegex.exec(blockedMatch[1])) !== null) {
    blockedStrs.push(m[1]);
  }

  // allowed 추출 -- 각 정규식 리터럴을 문자 단위로 스캔 (escaped slash 처리)
  const allowedMatch = content.match(/const\s+allowed\s*=\s*\[([\s\S]*?)\]/);
  if (!allowedMatch) throw new Error('allowed 배열 파싱 실패');
  const allowedPaths = [];
  const body = allowedMatch[1];
  let i = 0;
  while (i < body.length) {
    // 정규식 리터럴 시작 찾기: /^
    if (body[i] === '/' && body[i + 1] === '^') {
      let j = i + 2;
      let pattern = '';
      // 끝나는 / 찾기 (단, \/ 는 escape)
      while (j < body.length) {
        if (body[j] === '\\' && body[j + 1] === '/') {
          pattern += '\\/';
          j += 2;
        } else if (body[j] === '/') {
          break;
        } else {
          pattern += body[j];
          j++;
        }
      }
      if (j < body.length) {
        // 정규식 이스케이프 제거: \. → ., \/ → /
        let readable = pattern.replace(/\\\./g, '.').replace(/\\\//g, '/');
        if (readable.endsWith('$')) {
          readable = readable.slice(0, -1);
        } else if (!readable.endsWith('/')) {
          readable = readable + '/';
        }
        allowedPaths.push(readable);
        i = j + 1;
        continue;
      }
    }
    i++;
  }

  const blockedRows = blockedStrs.map(p => {
    const desc = BLOCKED_DESC[p] || '(설명 미등록)';
    return `| \`${escapeMdCell(p)}\` | ${escapeMdCell(desc)} |`;
  });

  const allowedRows = allowedPaths.map(p => {
    const desc = ALLOWED_DESC[p] || '(설명 미등록)';
    return `| \`${escapeMdCell(p)}\` | ${escapeMdCell(desc)} |`;
  });

  const lines = [
    '',
    `**차단 경로** (${blockedStrs.length}개):`,
    '',
    '| 경로 | 이유 |',
    '|------|------|',
    ...blockedRows,
    '',
    `**허용 경로** (${allowedPaths.length}개 패턴):`,
    '',
    '| 패턴 | 용도 |',
    '|------|------|',
    ...allowedRows,
    '',
    '**특수**: `../001_Wiki_AI/` (위키 형제 디렉토리, IMP-005)'
  ];
  return lines.join('\n');
}

// --- Reader 6: bkit 스크립트 ---
function readBkitScripts(cwd) {
  const scriptsDir = path.join(cwd, '.bkit', 'plugin', 'scripts');
  if (!fs.existsSync(scriptsDir)) return null;

  const files = fs.readdirSync(scriptsDir)
    .filter(f => f.endsWith('.js'))
    .sort();

  // 카테고리별 분류
  const buckets = {};
  for (const rule of CATEGORY_RULES) {
    buckets[rule.cat] = [];
  }

  for (const f of files) {
    for (const rule of CATEGORY_RULES) {
      if (rule.match.test(f)) {
        buckets[rule.cat].push(f);
        break;
      }
    }
  }

  const rows = [];
  for (const rule of CATEGORY_RULES) {
    const bucket = buckets[rule.cat];
    if (bucket.length === 0) continue;
    const preview = bucket.slice(0, 3).join(', ') + (bucket.length > 3 ? ' 등' : '');
    rows.push(`| **${rule.cat}** | ${escapeMdCell(preview)} | ${bucket.length} |`);
  }

  const header = [
    '',
    `전체 ${files.length}개 스크립트`,
    '',
    '| 카테고리 | 스크립트 | 수량 |',
    '|----------|---------|------|'
  ];
  return header.concat(rows).join('\n');
}

// --- 엔진: AUTO 마커 사이 내용 교체 ---
function replaceAutoSection(navContent, marker, newContent) {
  const startTag = `<!-- AUTO:${marker}:START -->`;
  const endTag = `<!-- AUTO:${marker}:END -->`;
  const startIdx = navContent.indexOf(startTag);
  const endIdx = navContent.indexOf(endTag);
  if (startIdx === -1 || endIdx === -1 || endIdx < startIdx) {
    throw new Error(`Marker ${marker} not found or malformed`);
  }
  const before = navContent.slice(0, startIdx + startTag.length);
  const after = navContent.slice(endIdx);
  return before + '\n' + newContent + '\n' + after;
}

// --- 엔진: 원자적 쓰기 + 백업 ---
function atomicWriteWithBackup(filePath, content) {
  const backup = filePath + '.bak';
  const tmp = filePath + '.tmp.' + Date.now() + '.' + Math.floor(Math.random() * 10000);
  try {
    if (fs.existsSync(filePath)) {
      fs.copyFileSync(filePath, backup);
    }
    fs.writeFileSync(tmp, content, 'utf8');
    fs.renameSync(tmp, filePath);
  } catch (e) {
    try { if (fs.existsSync(tmp)) fs.unlinkSync(tmp); } catch (_) {}
    throw e;
  }
}

// --- 엔진: 갱신 이력 추가 ---
function appendHistory(navPath, label, relFile, status) {
  try {
    let content = fs.readFileSync(navPath, 'utf8');
    const historyMarker = '| 날짜 | 변경 내용 | 트리거 |';
    const historyIdx = content.lastIndexOf(historyMarker);
    if (historyIdx === -1) return;

    const tableEnd = content.indexOf('\n\n', historyIdx);
    if (tableEnd === -1) return;

    const timestamp = new Date().toISOString().slice(0, 10);
    const statusLabel = status === 'success' ? '갱신 완료'
                      : status === 'reader-failed' ? '리더 실패 (이력만)'
                      : status === 'replace-failed' ? '교체 실패'
                      : status;
    const newRow = '\n| ' + timestamp + ' | ' + label + ' ' + statusLabel + ' | ' + relFile + ' 변경 |';
    content = content.slice(0, tableEnd) + newRow + content.slice(tableEnd);
    fs.writeFileSync(navPath, content, 'utf8');
  } catch (e) {
    // 이력 실패는 무시
  }
}

// =============================================================================
// Navigator Scaffold Generator (Phase B: Tier-A 확장 도구)
// extractSkillStructure / extractPreservedSections / generateBlockCardSkeleton
// mergeNavigator / generateNavigatorScaffold
// =============================================================================

// --- slugify: 한글/영문 혼합 헤딩을 앵커 ID로 변환 ---
function slugify(s) {
  if (!s) return 'node';
  return s
    .toLowerCase()
    .replace(/[\s\u00a0]+/g, '-')
    .replace(/[^\w\-가-힣]/g, '')
    .replace(/\-+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 60);
}

// --- extractSkillStructure(cwd, skillName) -> 구조 객체 ---
function extractSkillStructure(cwd, skillName) {
  const skillPath = path.join(cwd, '.agents', 'skills', skillName, 'SKILL.md');
  if (!fs.existsSync(skillPath)) {
    throw new Error('SKILL.md not found: ' + skillPath);
  }
  const content = fs.readFileSync(skillPath, 'utf8');
  const fm = parseFrontmatter(content);

  // 프론트매터 이후 본문
  const bodyStart = content.indexOf('\n---', 4);
  const body = bodyStart !== -1 ? content.slice(bodyStart + 4) : content;
  const lines = body.split(/\r?\n/);

  // 섹션 헤더 추출 (## + ###)
  const sections = [];
  let currentSection = null;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const m = line.match(/^(#{2,4})\s+(.+?)\s*$/);
    if (m) {
      if (currentSection) {
        currentSection.lineEnd = i - 1;
        currentSection.body = lines.slice(currentSection.lineStart + 1, i).join('\n').trim();
        sections.push(currentSection);
      }
      currentSection = {
        level: m[1].length,
        heading: m[2].trim(),
        lineStart: i,
        lineEnd: -1,
        body: ''
      };
    }
  }
  if (currentSection) {
    currentSection.lineEnd = lines.length - 1;
    currentSection.body = lines.slice(currentSection.lineStart + 1).join('\n').trim();
    sections.push(currentSection);
  }

  // 패턴 감지 (Track / Phase / Step / Operation)
  const phases = [];
  const tracks = [];
  const steps = [];
  for (const section of sections) {
    const h = section.heading;
    const trackMatch = h.match(/^\[?Track\s+([A-Z])\]?\s*(.*)$/i);
    if (trackMatch) {
      tracks.push({
        id: trackMatch[1],
        name: trackMatch[2] || h,
        description: firstLine(section.body)
      });
      continue;
    }
    const phaseMatch = h.match(/^Phase\s+(-?\d+|[A-Z]|[가-힣])[:.]?\s*(.*)$/i);
    if (phaseMatch) {
      phases.push({
        id: phaseMatch[1],
        name: phaseMatch[2] || h,
        description: firstLine(section.body)
      });
      continue;
    }
    const stepMatch = h.match(/^Step\s+(\d+)[:.]?\s*(.*)$/i);
    if (stepMatch) {
      steps.push({
        id: stepMatch[1],
        name: stepMatch[2] || h,
        description: firstLine(section.body)
      });
      continue;
    }
  }

  // 프로세스 타입 결정 (우선순위: track > phase > step > linear)
  let processType = 'linear';
  if (tracks.length >= 2) processType = 'track';
  else if (phases.length >= 2) processType = 'phase';
  else if (steps.length >= 2) processType = 'step';

  return {
    frontmatter: fm,
    sections: sections,
    phases: phases.length > 0 ? phases : null,
    tracks: tracks.length > 0 ? tracks : null,
    steps: steps.length > 0 ? steps : null,
    processType: processType,
    skillName: skillName
  };
}

// --- extractPreservedSections(existingNavPath) -> {scenarios, constraints, history} ---
function extractPreservedSections(existingNavPath) {
  if (!existingNavPath || !fs.existsSync(existingNavPath)) {
    return { scenarios: null, constraints: null, history: [] };
  }
  const content = fs.readFileSync(existingNavPath, 'utf8');
  const lines = content.split(/\r?\n/);

  // 섹션 경계 탐지 (## 헤딩)
  const sectionStarts = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^##\s+(?:\d+\.?\s+)?(.+?)\s*$/);
    if (m) {
      sectionStarts.push({ index: i, heading: m[1].trim() });
    }
  }

  const sliceSection = (startIdx) => {
    const start = sectionStarts[startIdx];
    const next = sectionStarts[startIdx + 1];
    const endIdx = next ? next.index : lines.length;
    return lines.slice(start.index, endIdx).join('\n').trim();
  };

  let scenarios = null;
  let constraints = null;
  for (let i = 0; i < sectionStarts.length; i++) {
    const h = sectionStarts[i].heading;
    // IMP-019: SECTION_PATTERNS 상수 사용 (섹션명 변형 대응)
    if (SECTION_PATTERNS.scenarios.test(h) && !scenarios) {
      scenarios = sliceSection(i);
    }
    if (SECTION_PATTERNS.constraints.test(h) && !constraints) {
      constraints = sliceSection(i);
    }
  }

  // 갱신 이력 테이블 파싱
  const history = [];
  const historyHeaderIdx = content.indexOf('| 날짜 | 변경');
  if (historyHeaderIdx !== -1) {
    const tail = content.slice(historyHeaderIdx);
    const tailLines = tail.split(/\r?\n/);
    // 헤더 + 구분선 이후 데이터 행
    for (let i = 2; i < tailLines.length; i++) {
      const line = tailLines[i].trim();
      if (!line.startsWith('|')) break;
      const cells = line.split('|').map(s => s.trim()).filter(Boolean);
      if (cells.length >= 2) {
        history.push({
          date: cells[0] || '',
          change: cells[1] || '',
          trigger: cells[2] || ''
        });
      }
    }
  }

  return { scenarios, constraints, history };
}

// --- generateMermaidTemplateByPattern(processType, structure) -> Mermaid markdown string ---
// IMP-019 (b): 4종 패턴별 Mermaid 템플릿 (Track / Linear / Branching+Phase / Conditional Step)
// 공통: ELK 렌더러 + securityLevel loose + classDef warning/io + click 자동 생성
function generateMermaidTemplateByPattern(processType, structure) {
  const out = [];
  out.push('```mermaid');
  out.push('%%{init: {"flowchart": {"defaultRenderer": "elk"}, "securityLevel": "loose"} }%%');
  out.push('flowchart TD');

  const clicks = [];
  const pushClick = (id, anchor) => clicks.push('    click ' + id + ' "#' + anchor + '"');

  if (processType === 'track' && structure.tracks && structure.tracks.length >= 2) {
    // === Track 패턴 (Decision Tree) ===
    out.push('    Start([사용자 호출]):::io --> Q1{진입 조건?}');
    pushClick('Start', 'node-start');
    pushClick('Q1', 'node-q1');
    structure.tracks.forEach((t, idx) => {
      const nodeId = 'Track' + t.id;
      const nameShort = truncate(t.name || ('Track ' + t.id), 30);
      const condLabel = '조건 ' + t.id;
      out.push('    Q1 -->|' + condLabel + '| ' + nodeId + '[Track ' + t.id + '<br/>' + escapeMdCell(nameShort) + ']');
      out.push('    ' + nodeId + ' --> End');
      pushClick(nodeId, 'node-track-' + t.id.toLowerCase());
    });
    out.push('    End([완료]):::io');
    pushClick('End', 'node-end');
  } else if (processType === 'phase' && structure.phases && structure.phases.length >= 2) {
    // === Branching + Phase 패턴 (Mode 분기 또는 단순 Phase 순차) ===
    // Mode 키워드 감지: 섹션 이름이나 본문에 "Mode"/"모드"가 있으면 분기, 없으면 선형
    const hasModeHint = (structure.sections || []).some(s => /mode|모드/i.test(s.heading));
    if (hasModeHint) {
      out.push('    Start([진입]):::io --> ModeCheck{모드 선택?}');
      pushClick('Start', 'node-start');
      pushClick('ModeCheck', 'node-mode-check');
      out.push('    ModeCheck -->|Mode A<br/>전체| FullP1[Phase 1]');
      // 감지된 Phase를 Mode A의 순차로 나열
      structure.phases.forEach((p, idx) => {
        const curId = 'FullP' + (idx + 1);
        const nextId = idx < structure.phases.length - 1 ? 'FullP' + (idx + 2) : 'End';
        const nameShort = truncate(p.name || ('Phase ' + p.id), 30);
        if (idx > 0) {
          out.push('    ' + curId + '[Phase ' + p.id + '<br/>' + escapeMdCell(nameShort) + '] --> ' + nextId);
        }
        pushClick(curId, 'node-full-p' + p.id);
      });
      out.push('    ModeCheck -->|Mode B<br/>간단| ShortPath[Append 경로] --> End');
      pushClick('ShortPath', 'node-short');
    } else {
      // 단순 Phase 순차
      out.push('    Start([진입]):::io --> P1');
      pushClick('Start', 'node-start');
      structure.phases.forEach((p, idx) => {
        const curId = 'P' + (idx + 1);
        const nextId = idx < structure.phases.length - 1 ? 'P' + (idx + 2) : 'End';
        const nameShort = truncate(p.name || ('Phase ' + p.id), 30);
        out.push('    ' + curId + '[Phase ' + p.id + '<br/>' + escapeMdCell(nameShort) + '] --> ' + nextId);
        pushClick(curId, 'node-p' + p.id);
      });
    }
    out.push('    End([완료]):::io');
    pushClick('End', 'node-end');
  } else if (processType === 'step' && structure.steps && structure.steps.length >= 2) {
    // === Conditional Step 패턴 (Yes/No 분기로 각 단계 생략 가능) ===
    out.push('    Start([사용자 요청]):::io --> Q1{Step 1<br/>필요?}');
    pushClick('Start', 'node-start');
    structure.steps.forEach((s, idx) => {
      const qId = 'Q' + (idx + 1);
      const sId = 'S' + (idx + 1);
      const nameShort = truncate(s.name || ('Step ' + s.id), 30);
      const nextQ = idx < structure.steps.length - 1 ? 'Q' + (idx + 2) : 'End';
      out.push('    ' + qId + ' -->|Yes| ' + sId + '[Step ' + s.id + '<br/>' + escapeMdCell(nameShort) + ']');
      out.push('    ' + qId + ' -->|No| ' + nextQ);
      out.push('    ' + sId + ' --> ' + nextQ);
      // 다음 Q 노드의 정의 (마지막 Step이 아니면)
      if (idx < structure.steps.length - 1) {
        const nextIdx = idx + 2;
        const nextStep = structure.steps[idx + 1];
        out.push('    Q' + nextIdx + '{Step ' + nextStep.id + '<br/>필요?}');
      }
      pushClick(qId, 'node-q' + s.id);
      pushClick(sId, 'node-step-' + s.id);
    });
    out.push('    End([완료]):::io');
    pushClick('End', 'node-end');
  } else {
    // === Linear Pipeline 패턴 (기본) ===
    // level=2 sections 중 앞쪽 3-8개를 파이프라인 단계로
    const stageSections = (structure.sections || [])
      .filter(s => s.level === 2)
      .filter(s => !SECTION_PATTERNS.scenarios.test(s.heading) && !SECTION_PATTERNS.constraints.test(s.heading))
      .slice(0, 8);
    if (stageSections.length >= 2) {
      out.push('    Start([입력]):::io --> S1');
      pushClick('Start', 'node-start');
      stageSections.forEach((s, idx) => {
        const curId = 'S' + (idx + 1);
        const nextId = idx < stageSections.length - 1 ? 'S' + (idx + 2) : 'End';
        const nameShort = truncate(s.heading, 30);
        out.push('    ' + curId + '[' + escapeMdCell(nameShort) + '] --> ' + nextId);
        pushClick(curId, 'node-' + slugify(s.heading));
      });
      out.push('    End([출력]):::io');
      pushClick('End', 'node-end');
    } else {
      // Fallback: generic placeholder
      out.push('    Start([사용자 호출]):::io --> TODO[(TODO: SKILL.md 기반 수동 작성)]');
      out.push('    TODO --> End([완료]):::io');
      pushClick('Start', 'node-start');
      pushClick('TODO', 'node-todo');
      pushClick('End', 'node-end');
    }
  }

  out.push('');
  clicks.forEach(c => out.push(c));
  out.push('');
  out.push('    classDef warning fill:#fee,stroke:#c00,stroke-width:2px');
  out.push('    classDef io fill:#eef,stroke:#338,stroke-width:2px');
  out.push('```');
  return out.join('\n');
}

// --- extractContextAroundKeyword(body, pattern) -> 키워드 주변 문장 추출 ---
// IMP-019 (c): 결정론적 힌트 추론 (LLM 호출 없음)
function extractContextAroundKeyword(body, pattern) {
  if (!body) return null;
  // 문장 단위 분할 (한국어 마침표 포함)
  const sentences = body.split(/[.!?。\n]+/).map(s => s.trim()).filter(Boolean);
  for (const s of sentences) {
    if (pattern.test(s)) return s;
  }
  return null;
}

// --- inferBlockCardHints(section, structure) -> {motivationHint, actionHint, status, fileMatches} ---
function inferBlockCardHints(section, structure) {
  const body = section.body || '';
  const firstSentence = body.split(/[.!?。\n]/)[0].trim();

  // 1. 동기 힌트: "목적"/"이유"/"때문에" 등 키워드 주변 문장
  const motivationKeywords = /목적|이유|때문에|위해|필요|해결|동기|문제|방지|보장/;
  const motivationHint = extractContextAroundKeyword(body, motivationKeywords) || firstSentence;

  // 2. 동작 방식 힌트: 동사형 키워드 주변 문장
  const actionKeywords = /호출|실행|수행|생성|저장|처리|변환|검사|입력|출력|전달|반환|계산|파싱|갱신|이동/;
  const actionHint = extractContextAroundKeyword(body, actionKeywords);

  // 3. 상태 힌트: "[작동]"/"[미구현]"/"[부분]" 스캔
  const statusMatch = body.match(/\[(작동|부분|미구현)\]/);
  const status = statusMatch ? '[' + statusMatch[1] + ']' : '[작동]';

  // 4. 관련 파일: `경로` 패턴 스캔 (백틱으로 감싸진 .md/.js/.py/.json 파일)
  const fileRegex = /`([^`]+\.(?:md|js|py|json|sh|yml|yaml))`/g;
  const fileMatches = [];
  let fm;
  while ((fm = fileRegex.exec(body)) !== null) {
    fileMatches.push(fm[1]);
  }

  return { motivationHint, actionHint, status, fileMatches };
}

// --- generateBlockCardSkeleton(section, processType, skillName) -> markdown 블럭 카드 ---
function generateBlockCardSkeleton(section, processType, skillName) {
  const anchor = 'node-' + slugify(section.heading);
  const bodyPreview = truncate(firstLine(section.body) || '(SKILL.md 본문 참조)', 100);

  // IMP-019 (c): 결정론적 힌트 추론으로 TODO placeholder 강화
  const hints = inferBlockCardHints(section, null);
  const motivationCell = hints.motivationHint
    ? '(TODO: 다음 문장 기반 정제) ' + escapeMdCell(truncate(hints.motivationHint, 120))
    : '(TODO: SKILL.md 기반 수동 작성)';
  const actionCell = hints.actionHint
    ? '(TODO: 다음 힌트 기반 구체화) ' + escapeMdCell(truncate(hints.actionHint, 120))
    : '(TODO: 수동 작성)';
  const fileCell = hints.fileMatches.length > 0
    ? hints.fileMatches.slice(0, 3).map(f => '`' + f + '`').join(', ')
    : '`.agents/skills/' + skillName + '/SKILL.md`';

  const rows = [
    '### ' + section.heading + ' {#' + anchor + '}',
    '',
    '| 항목 | 내용 |',
    '|------|------|',
    '| 소속 | ' + processType + ' 구조 |',
    '| 동기 | ' + motivationCell + ' |',
    '| 내용 | ' + escapeMdCell(bodyPreview) + ' |',
    '| 동작 방식 | ' + actionCell + ' |',
    '| 상태 | ' + hints.status + ' |',
    '| 관련 파일 | ' + fileCell + ' |',
    '',
    '[다이어그램으로 복귀](#전체-체계도)',
    ''
  ];
  return rows.join('\n');
}

// --- generateNavigatorScaffold(cwd, skillName, options) -> markdown string ---
function generateNavigatorScaffold(cwd, skillName, options) {
  options = options || {};
  const preserveExisting = options.preserveExisting !== false;
  const appendHistoryRow = options.appendHistoryRow !== false;

  const structure = extractSkillStructure(cwd, skillName);
  const navPath = path.join(cwd, '.agents', 'skills', skillName, skillName + '_Navigator.md');
  const preserved = preserveExisting
    ? extractPreservedSections(navPath)
    : { scenarios: null, constraints: null, history: [] };

  const today = new Date().toISOString().slice(0, 10);
  const processType = structure.processType;
  const tierInfo = TIER_MAP[skillName] || { tier: 'B', command: '자동 트리거', desc: structure.frontmatter.description || '' };

  // === Header + Legend ===
  const out = [];
  out.push('# ' + skillName + ' -- Navigator');
  out.push('');
  out.push('> SYSTEM_NAVIGATOR 스타일 시각적 네비게이터');
  out.push('> 최종 갱신: ' + today + ' (scaffold 자동 생성)');
  out.push('> SKILL.md와 교차 참조 (이 파일은 SKILL.md의 시각화 계층)');
  out.push('');
  out.push('---');
  out.push('');
  out.push('## 0. 범례 + 사용법 {#범례--사용법}');
  out.push('');
  out.push('### 상태 표시');
  out.push('');
  out.push('| 표시 | 의미 |');
  out.push('|------|------|');
  out.push('| **[작동]** | 정상 작동 중 |');
  out.push('| **[부분]** | 일부만 작동 |');
  out.push('| **[미구현]** | 설계만 있고 구현 없음 |');
  out.push('');
  out.push('### 다이어그램 규약');
  out.push('');
  out.push('- ISO 5807:1985 표준 기호 준수');
  out.push('- Mermaid ELK 렌더러 + `securityLevel: loose`');
  out.push('- 점선 `-.->` = 피드백 루프 (재시도/복귀)');
  out.push('- `:::warning` = 에러/차단/실패 블럭');
  out.push('- `click NODE "#anchor"` = 블럭 상세 카드로 이동');
  out.push('');
  out.push('### 스킬 메타');
  out.push('');
  out.push('| 항목 | 값 |');
  out.push('|------|-----|');
  out.push('| 이름 | ' + skillName + ' |');
  out.push('| Tier | ' + tierInfo.tier + ' |');
  out.push('| 커맨드 | ' + tierInfo.command + ' |');
  out.push('| 프로세스 타입 | ' + processType + ' |');
  out.push('| 설명 | ' + escapeMdCell(truncate(firstLine(structure.frontmatter.description || ''), 120)) + ' |');
  out.push('');
  out.push('---');
  out.push('');

  // === §1 전체 체계도 (placeholder) ===
  out.push('## 1. 전체 워크플로우 체계도 {#전체-체계도}');
  out.push('');
  out.push('<!-- AUTO:DIAGRAM_MAIN:START -->');
  out.push('');
  // IMP-019 (b): 패턴별 Mermaid 템플릿 자동 생성
  out.push(generateMermaidTemplateByPattern(processType, structure));
  out.push('');
  out.push('> **TODO (피드백 루프 + 세부화)**: 위 Mermaid는 ' + processType + ' 패턴 기본 뼈대. 피드백 루프(`-.->`), 분기 조건, 에러 복구 경로를 수동 보완하세요.');
  if (structure.tracks) {
    out.push('> 감지된 Track: ' + structure.tracks.map(t => t.id + ' (' + truncate(t.name, 30) + ')').join(', '));
  }
  if (structure.phases) {
    out.push('> 감지된 Phase: ' + structure.phases.map(p => p.id).join(', '));
  }
  if (structure.steps) {
    out.push('> 감지된 Step: ' + structure.steps.map(s => s.id).join(', '));
  }
  out.push('');
  out.push('<!-- AUTO:DIAGRAM_MAIN:END -->');
  out.push('');

  // 블럭 바로가기 Fallback
  out.push('<details><summary><strong>블럭 바로가기 (다이어그램 클릭 대안)</strong></summary>');
  out.push('');
  const shortcuts = structure.sections
    .filter(s => s.level === 2 || s.level === 3)
    .map(s => '[' + s.heading + '](#node-' + slugify(s.heading) + ')')
    .join(' · ');
  out.push(shortcuts || '(TODO: 블럭 바로가기 목록 수동 보완)');
  out.push(' · [**전체 블럭 카탈로그**](#block-catalog)');
  out.push('');
  out.push('</details>');
  out.push('');
  out.push('[맨 위로](#범례--사용법)');
  out.push('');
  out.push('---');
  out.push('');

  // === §2 블럭 상세 카탈로그 ===
  out.push('## 2. 블럭 상세 카탈로그 {#block-catalog}');
  out.push('');
  out.push('<details><summary>블럭 카드 펼치기</summary>');
  out.push('');
  for (const section of structure.sections) {
    if (section.level === 2 || section.level === 3) {
      out.push(generateBlockCardSkeleton(section, processType, skillName));
    }
  }
  out.push('</details>');
  out.push('');
  out.push('[맨 위로](#범례--사용법)');
  out.push('');
  out.push('---');
  out.push('');

  // === §3 사용 시나리오 (보존 or placeholder) ===
  if (preserved.scenarios) {
    // 보존된 섹션을 그대로 삽입 (헤딩은 재번호 매기기 위해 교체)
    const preservedBody = preserved.scenarios.replace(/^##\s+(?:\d+\.?\s+)?/, '## 3. ');
    out.push(preservedBody);
    out.push('');
  } else {
    out.push('## 3. 사용 시나리오');
    out.push('');
    out.push('### 시나리오 1 (TODO)');
    out.push('');
    out.push('(TODO: 수동 작성)');
    out.push('');
    out.push('### 시나리오 2 (TODO)');
    out.push('');
    out.push('(TODO: 수동 작성)');
    out.push('');
    out.push('### 시나리오 3 (TODO)');
    out.push('');
    out.push('(TODO: 수동 작성)');
    out.push('');
  }
  out.push('[맨 위로](#범례--사용법)');
  out.push('');
  out.push('---');
  out.push('');

  // === §4 제약사항 (보존 or placeholder) ===
  if (preserved.constraints) {
    const preservedBody = preserved.constraints.replace(/^##\s+(?:\d+\.?\s+)?/, '## 4. ');
    out.push(preservedBody);
    out.push('');
  } else {
    out.push('## 4. 제약사항');
    out.push('');
    out.push('- (TODO: SKILL.md 기반 제약사항 수동 작성)');
    out.push('- 이모티콘 금지');
    out.push('- 절대경로 금지');
    out.push('');
  }
  out.push('[맨 위로](#범례--사용법)');
  out.push('');
  out.push('---');
  out.push('');

  // === §5 갱신 이력 (병합) ===
  out.push('## 5. 갱신 이력');
  out.push('');
  out.push('| 날짜 | 변경 | 트리거 |');
  out.push('|------|------|--------|');
  if (appendHistoryRow) {
    out.push('| ' + today + ' | scaffold 자동 생성 + 기존 시나리오/제약 보존 | generate-navigator-cli |');
  }
  for (const row of preserved.history) {
    if (row.date && row.change) {
      out.push('| ' + row.date + ' | ' + row.change + ' | ' + (row.trigger || '-') + ' |');
    }
  }
  out.push('');
  out.push('[맨 위로](#범례--사용법)');
  out.push('');

  return out.join('\n');
}

// --- mergeNavigator: 향후 확장 (현재는 generateNavigatorScaffold가 내부 병합) ---
function mergeNavigator(scaffold, preserved, options) {
  // 현재 구현: scaffold가 이미 preserved를 포함하므로 passthrough
  // 향후 부분 업데이트 지원 시 확장
  return scaffold;
}

module.exports = {
  parseFrontmatter,
  firstLine,
  truncate,
  readSkillsCatalog,
  readMcpServers,
  readCommands,
  readImprints,
  readPreToolGuard,
  readBkitScripts,
  replaceAutoSection,
  atomicWriteWithBackup,
  appendHistory,
  // Phase B scaffold tools
  slugify,
  extractSkillStructure,
  extractPreservedSections,
  generateBlockCardSkeleton,
  generateNavigatorScaffold,
  mergeNavigator,
  // IMP-019 scaffold 고도화 (Option B)
  SECTION_PATTERNS,
  generateMermaidTemplateByPattern,
  extractContextAroundKeyword,
  inferBlockCardHints
};
