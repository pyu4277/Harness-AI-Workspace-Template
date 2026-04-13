#!/usr/bin/env node
// =============================================================================
// token-budget.js -- 임의 문자열에 대한 토큰 예산 분석
// Reference-Port: MindVault 0/100/800 스펙만 차용
//
// 입력: stdin text
// 출력: stdout JSON { chars, approx_tokens, fits_layer: {0,100,800}, over_by? }
// =============================================================================

let buf = '';
process.stdin.on('data', c => buf += c);
process.stdin.on('end', () => {
  const text = buf;
  const chars = text.length;
  const approx = Math.max(1, Math.ceil(chars / 4));
  const layers = [0, 100, 800];
  const fits = {};
  for (const L of layers) fits[L] = approx <= L;
  const over = {};
  for (const L of layers) if (!fits[L]) over[L] = approx - L;

  process.stdout.write(JSON.stringify({
    chars,
    approx_tokens: approx,
    fits_layer: fits,
    over_by: over,
  }));
});
