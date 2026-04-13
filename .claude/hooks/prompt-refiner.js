// =============================================================================
// Harness: UserPromptSubmit - Prompt Refiner + Imprint Recall + Completion Injection
// 기둥 4 (피드백 루프): 프롬프트 정제 + 각인 회수 + 완료 체크리스트 주입
//
// 3가지 기능:
// 1. 각인 키워드 매칭 -> recall_count 증가 + stderr 알림
// 2. 용어사전 치환 -> 장황한 표현을 전문용어로 압축
// 3. 완료 체크리스트 주입 -> 작업성 프롬프트에 Feature Usage/용어/각인 체크리스트 삽입
// =============================================================================

const fs = require('fs');
const path = require('path');

const IMPRINTS_PATH = path.join(process.cwd(), '.harness', 'imprints.json');
const GLOSSARY_PATH = path.join(process.cwd(), 'docs', 'LogManagement', '용어사전.md');
const REFINE_LOG = path.join(process.cwd(), '.harness', 'refine-log.jsonl');
const PROMOTE_MD = path.join(process.cwd(), '..', '001_Wiki_AI', '990_Meta', 'promote-candidates.md');
const PROMOTE_THRESHOLD = 30;

// 작업성 프롬프트 감지 키워드 (이 키워드가 포함되면 완료 체크리스트 주입)
const TASK_KEYWORDS = [
  '만들어', '구현', '작성', '생성', '수정', '변경', '추가', '삭제', '설정',
  '분석', '검토', '설계', '기획', '개발', '배포', '테스트', '빌드',
  '인제스트', 'ingest', 'create', 'build', 'implement', 'fix', 'update',
  '해줘', '해주세요', '하자', '진행', '시작', '실행'
];

// 단순 질문 패턴 (이 패턴이면 체크리스트 주입 안 함)
const SIMPLE_PATTERNS = [
  /^(뭐야|뭐해|뭘|어떻게|왜|언제|어디|누구)\?*$/,
  /^(네|아니|ㅇㅇ|ㅇㅋ|오케이|ok|yes|no)\?*$/i,
  /^.{0,7}$/  // 7자 이하 단문 (한국어는 짧으므로 임계값 낮춤)
];

let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const hookData = JSON.parse(input);
    let userMessage = hookData.message || '';

    if (!userMessage || userMessage.length < 3) {
      process.exit(0);
    }

    const modifications = [];

    // ========================================
    // 1. 각인 키워드 매칭 + recall_count 증가
    // ========================================
    if (fs.existsSync(IMPRINTS_PATH)) {
      try {
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

        if (matched.length > 0) {
          matched.sort((a, b) => b.hitCount - a.hitCount);
          const top = matched.slice(0, 3);

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

          for (const m of top) {
            process.stderr.write(
              '[각인 ' + m.imp.id + '] ' + m.imp.principle + ' (매칭: ' + m.hits.join(', ') + ')\n'
            );
          }
        }
      } catch (e) {
        // 각인 처리 실패 시 조용히 통과
      }
    }

    // ========================================
    // 2. PromptRefinementGate (warn+substitute) — Phase 0 IMP-027
    //    용어사전 매칭 → stderr 힌트 + refine-log.jsonl 누적 + 30회 도달 시 로드맵 생성.
    //    원문은 파괴하지 않는다 (warn 모드). 치환본은 다음 턴 참고용.
    // ========================================
    if (fs.existsSync(GLOSSARY_PATH)) {
      try {
        const glossary = fs.readFileSync(GLOSSARY_PATH, 'utf8');
        const termRows = glossary.match(/\|[^|]+\|[^|]+\|/g) || [];
        const termsApplied = [];

        for (const row of termRows) {
          const cells = row.split('|').map(c => c.trim()).filter(c => c);
          if (cells.length >= 2) {
            const term = cells[0];
            const original = cells[1];
            if (term === '전문용어' || original === '원문') continue;
            if (original && original.length >= 4 && userMessage.includes(original) && term !== original) {
              termsApplied.push({ from: original, to: term });
            }
          }
        }

        if (termsApplied.length > 0) {
          // 압축본 생성 (긴 원문부터 적용)
          let compressed = userMessage;
          const sorted = [...termsApplied].sort((a, b) => b.from.length - a.from.length);
          for (const t of sorted) compressed = compressed.split(t.from).join(t.to);

          const termNote = termsApplied
            .map(t => '"' + t.from + '" -> "' + t.to + '"')
            .join(', ');
          process.stderr.write('[HINT 압축 제안] ' + termNote + '\n');
          process.stderr.write('[HINT compressed] ' + compressed.slice(0, 200) +
            (compressed.length > 200 ? ' ...' : '') + '\n');

          // refine-log.jsonl 누적
          try {
            fs.mkdirSync(path.dirname(REFINE_LOG), { recursive: true });
            fs.appendFileSync(REFINE_LOG, JSON.stringify({
              ts: new Date().toISOString(),
              original_len: userMessage.length,
              compressed_len: compressed.length,
              hits: termsApplied.map(t => ({ from: t.from, to: t.to })),
            }) + '\n', 'utf8');
          } catch { /* noop */ }

          // 30회 도달 시 promote-candidates.md 생성
          try {
            const logText = fs.existsSync(REFINE_LOG)
              ? fs.readFileSync(REFINE_LOG, 'utf8')
              : '';
            const lineCount = logText.split('\n').filter(l => l.trim()).length;
            if (lineCount >= PROMOTE_THRESHOLD && lineCount % PROMOTE_THRESHOLD === 0) {
              const recent = logText.split('\n').filter(l => l.trim()).slice(-PROMOTE_THRESHOLD);
              const freq = new Map();
              for (const line of recent) {
                try {
                  const rec = JSON.parse(line);
                  for (const h of (rec.hits || [])) {
                    freq.set(h.to, (freq.get(h.to) || 0) + 1);
                  }
                } catch { /* noop */ }
              }
              const top = [...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10);
              const body = [
                '# 프롬프트 압축 승격 후보 (auto-generated)',
                '',
                '- 생성: ' + new Date().toISOString(),
                '- 로그 총 ' + lineCount + '건 중 최근 ' + PROMOTE_THRESHOLD + '건 분석',
                '',
                '| 전문용어 | 빈도 |',
                '|----------|------|',
                ...top.map(([t, f]) => '| ' + t + ' | ' + f + ' |'),
              ].join('\n');
              fs.mkdirSync(path.dirname(PROMOTE_MD), { recursive: true });
              fs.writeFileSync(PROMOTE_MD, body, 'utf8');
              process.stderr.write('[로드맵 생성] ' + PROMOTE_MD + '\n');
            }
          } catch { /* noop */ }

          modifications.push('term_substitution');
        }
      } catch (e) {
        // 용어사전 처리 실패 시 조용히 통과
      }
    }

    // ========================================
    // 3. 완료 체크리스트 주입 (작업성 프롬프트만)
    // ========================================
    const isSimple = SIMPLE_PATTERNS.some(p => p.test(userMessage.trim()));
    const isTask = !isSimple && TASK_KEYWORDS.some(kw => userMessage.includes(kw));

    if (isTask && userMessage.length > 10) {
      // 작업성 프롬프트에 완료 체크리스트 주입
      const checklist = '\n\n[하네스 자동 주입 -- 작업 완료 시 반드시 수행]\n' +
        '1. Feature Usage 요약 출력 (Used: 사용한 도구/스킬, Not Used: 미사용 도구, Recommended: 추천 후속 작업)\n' +
        '2. 세션 중 발견한 전문용어가 있으면 term-organizer로 용어사전 등록\n' +
        '3. 에러/재시도/번거로운 작업이 있었으면 /imprint record로 각인 등록\n' +
        '4. 프롬프트가 모호하거나 개선 가능하면, 개선된 프롬프트를 먼저 제시 후 사용자 승인받고 진행';

      userMessage = userMessage + checklist;
      modifications.push('completion_checklist');
      process.stderr.write('[하네스] 작업성 프롬프트 감지 -> 완료 체크리스트 주입\n');
    }

    // ========================================
    // 4. 프롬프트 정제 필요성 판단
    // ========================================
    // 50자 이상이면서 구체적 행동 지시가 없는 경우
    if (userMessage.length > 50 && !isTask && !isSimple) {
      userMessage = userMessage + '\n\n[하네스 자동 주입: 이 요청이 모호하면 구체화된 버전을 먼저 제시하세요]';
      modifications.push('refine_flag');
      process.stderr.write('[하네스] 모호한 프롬프트 감지 -> 정제 플래그 주입\n');
    }

    // ========================================
    // 출력: 수정된 프롬프트 반환
    // ========================================
    if (modifications.length > 0) {
      console.log(JSON.stringify({ message: userMessage }));
    }
    // 수정 없으면 아무 출력 없이 종료 (원본 유지)

  } catch (e) {
    // 실패 시 조용히 통과 (원본 프롬프트 유지)
  }
});
