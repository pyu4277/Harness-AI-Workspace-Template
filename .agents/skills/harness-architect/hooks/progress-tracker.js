#!/usr/bin/env node
// Stop: 각 Phase 완료 시 진행 상태 저장
// 다음 Phase 안내 메시지 생성

const fs = require('fs');
const path = require('path');

async function main() {
  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  try {
    // 상태 파일 경로
    const stateDir = path.join(process.cwd(), '.claude', 'state');
    const statePath = path.join(stateDir, 'harness-state.json');

    if (!fs.existsSync(stateDir)) {
      fs.mkdirSync(stateDir, { recursive: true });
    }

    // 기존 상태 로드
    let state = {
      version: '1.0',
      project_name: '',
      current_phase: 0,
      phases: {
        '1_analyze': { status: 'pending', completed_at: null },
        '2_select': { status: 'pending', completed_at: null },
        '3_generate': { status: 'pending', completed_at: null },
        '4_design': { status: 'pending', completed_at: null },
        '5_review': { status: 'pending', completed_at: null },
        '6_iterate': { status: 'pending', completed_at: null },
        '7_install': { status: 'pending', completed_at: null }
      },
      generated_files: [],
      updated_at: new Date().toISOString()
    };

    if (fs.existsSync(statePath)) {
      try {
        state = JSON.parse(fs.readFileSync(statePath, 'utf-8'));
      } catch { /* 파싱 실패 시 기본값 사용 */ }
    }

    // 생성된 파일 감지로 Phase 진행 상태 추정
    const projectRoot = process.cwd();

    // Phase 1 완료 확인: 프로파일 존재
    const docsDir = path.join(projectRoot, 'docs');
    const claudeMd = path.join(projectRoot, 'CLAUDE.md');
    const settingsJson = path.join(projectRoot, '.claude', 'settings.local.json');

    if (fs.existsSync(docsDir)) {
      const docs = fs.readdirSync(docsDir).filter(f => f.endsWith('.md'));
      if (docs.length > 0) {
        state.phases['3_generate'].status = 'in_progress';
        state.generated_files = docs.map(f => `docs/${f}`);
        state.current_phase = Math.max(state.current_phase, 3);
      }
    }

    if (fs.existsSync(claudeMd)) {
      state.phases['4_design'].status = 'completed';
      state.current_phase = Math.max(state.current_phase, 4);
    }

    if (fs.existsSync(settingsJson)) {
      state.phases['4_design'].status = 'completed';
      state.current_phase = Math.max(state.current_phase, 4);
    }

    state.updated_at = new Date().toISOString();
    fs.writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf-8');

  } catch {
    // 상태 추적 실패는 조용히 넘김
  }

  process.stdout.write('{}');
  process.exit(0);
}

main();
