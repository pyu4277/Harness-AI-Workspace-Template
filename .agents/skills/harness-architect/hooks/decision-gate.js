#!/usr/bin/env node
// PostToolUse(AskUserQuestion): 결정 게이트에서 사용자 결정사항을 기록
// 훅 이벤트: PostToolUse — matcher: AskUserQuestion

const fs = require('fs');
const path = require('path');

async function main() {
  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  try {
    const data = JSON.parse(input);

    // AskUserQuestion 응답만 처리
    if (data.tool_name !== 'AskUserQuestion') {
      process.stdout.write('{}');
      process.exit(0);
    }

    const question = data.tool_input?.question || '';
    const answer = data.tool_result?.answer || data.tool_result || '';

    // 결정 게이트 패턴 감지 (G1~G5)
    const gatePatterns = [
      { gate: 'G1', pattern: /분류가 맞습니까|분석 결과/i },
      { gate: 'G2', pattern: /문서.*선택|추가.*제거/i },
      { gate: 'G3', pattern: /CLAUDE\.md.*검토|규칙.*적합/i },
      { gate: 'G4', pattern: /보안 설정|권한.*설정|설정.*진행/i },
      { gate: 'G5', pattern: /설치.*진행|설치합니까/i }
    ];

    let detectedGate = null;
    for (const { gate, pattern } of gatePatterns) {
      if (pattern.test(question)) {
        detectedGate = gate;
        break;
      }
    }

    if (detectedGate) {
      // 결정 기록 파일 경로
      const stateDir = path.join(process.cwd(), '.claude', 'state');
      const logPath = path.join(stateDir, 'decision-log.json');

      // 디렉토리 생성
      if (!fs.existsSync(stateDir)) {
        fs.mkdirSync(stateDir, { recursive: true });
      }

      // 기존 로그 로드
      let log = { decisions: [] };
      if (fs.existsSync(logPath)) {
        try {
          log = JSON.parse(fs.readFileSync(logPath, 'utf-8'));
        } catch { /* 파싱 실패 시 새로 시작 */ }
      }

      // 결정 기록 추가
      log.decisions.push({
        gate: detectedGate,
        question: question.substring(0, 200),
        answer: String(answer).substring(0, 200),
        timestamp: new Date().toISOString()
      });

      fs.writeFileSync(logPath, JSON.stringify(log, null, 2), 'utf-8');
    }
  } catch {
    // 파싱 실패 시 조용히 통과
  }

  process.stdout.write('{}');
  process.exit(0);
}

main();
