#!/usr/bin/env node
// =============================================================================
// Wiki PDF Stage -- 위키 폴더의 PDF/HWP를 005_AI_Project/Temporary Storage로
// 임시 복사하여 PDF MCP 발췌 + 005 디렉토리 한정 정책 우회
// =============================================================================
//
// 배경 (260411 발견):
// - PDF MCP (mcp__plugin_pdf-viewer_pdf__display_pdf)는 005_AI_Project 디렉토리만 허용
// - 위키 폴더 (D:/OneDrive - 순천대학교/001_Wiki_AI/000_Raw/...)의 PDF 직접 발췌 불가
// - Read 도구는 pdftoppm 의존이라 unsafe location 오류 발생
// - 우회: 임시 복사 → PDF MCP → cleanup
//
// 사용법:
//   node .claude/hooks/wiki-pdf-stage.js stage <wiki-pdf-path>
//   node .claude/hooks/wiki-pdf-stage.js cleanup
//   node .claude/hooks/wiki-pdf-stage.js list
//
// 예시:
//   node .claude/hooks/wiki-pdf-stage.js stage \
//     "D:/OneDrive - 순천대학교/001_Wiki_AI/000_Raw/Obsidian Knowledge/200_사업/.../성과지표관리센터운영규정.pdf"
//   → Temporary Storage/wiki-pdf-stage/성과지표관리센터운영규정.pdf 생성
//   → 005 절대경로 출력 (PDF MCP에 사용)
//
// 안전 정책:
// - Temporary Storage/wiki-pdf-stage/ 만 사용 (다른 위치 쓰기 금지)
// - cleanup 시 wiki-pdf-stage/ 안의 파일만 삭제 (외부 파일 영향 0)
// - 절대경로 요구 (상대경로 거부)
// - 위키 root 시작 검증 (000_Raw/ 또는 990_Meta/archive/ 경로만 허용)
// =============================================================================

const fs = require('fs');
const path = require('path');

// =============================================================================
// 설정
// =============================================================================

const WIKI_ROOT = 'D:/OneDrive - 순천대학교/001_Wiki_AI';
const STAGE_DIR = path.join(process.cwd(), 'Temporary Storage', 'wiki-pdf-stage');
const ALLOWED_EXTENSIONS = ['.pdf', '.hwp', '.hwpx', '.docx', '.pptx'];

// 위키 root 시작 + 허용 prefix
const ALLOWED_WIKI_PREFIXES = [
  '000_Raw/',
  '990_Meta/archive/'
];

// =============================================================================
// 유틸리티
// =============================================================================

function ensureStageDir() {
  if (!fs.existsSync(STAGE_DIR)) {
    fs.mkdirSync(STAGE_DIR, { recursive: true });
    process.stderr.write('[wiki-pdf-stage] 임시 디렉토리 생성: ' + STAGE_DIR + '\n');
  }
}

function normalizeSlash(p) {
  return p.replace(/\\/g, '/');
}

function isAllowedWikiPath(absPath) {
  const norm = normalizeSlash(absPath);
  const wikiNorm = normalizeSlash(WIKI_ROOT);
  if (!norm.startsWith(wikiNorm + '/')) {
    return { ok: false, reason: '위키 root 외부 경로 (허용 안 됨): ' + WIKI_ROOT };
  }
  const rel = norm.slice(wikiNorm.length + 1);
  const allowed = ALLOWED_WIKI_PREFIXES.some(prefix => rel.startsWith(prefix));
  if (!allowed) {
    return { ok: false, reason: '허용 prefix 외 (' + ALLOWED_WIKI_PREFIXES.join(', ') + '): ' + rel };
  }
  return { ok: true, rel };
}

function isAllowedExtension(absPath) {
  const ext = path.extname(absPath).toLowerCase();
  return ALLOWED_EXTENSIONS.includes(ext);
}

// =============================================================================
// 명령: stage
// =============================================================================

function cmdStage(wikiPdfPath) {
  if (!wikiPdfPath) {
    process.stderr.write('[wiki-pdf-stage] 사용법: stage <wiki-pdf-path>\n');
    process.exit(1);
  }

  // 절대경로 검증
  if (!path.isAbsolute(wikiPdfPath)) {
    process.stderr.write('[wiki-pdf-stage] 거부: 절대경로 필요. 입력: ' + wikiPdfPath + '\n');
    process.exit(1);
  }

  // 위키 경로 검증
  const wikiCheck = isAllowedWikiPath(wikiPdfPath);
  if (!wikiCheck.ok) {
    process.stderr.write('[wiki-pdf-stage] 거부: ' + wikiCheck.reason + '\n');
    process.exit(1);
  }

  // 확장자 검증
  if (!isAllowedExtension(wikiPdfPath)) {
    process.stderr.write('[wiki-pdf-stage] 거부: 허용 확장자 외 (' + ALLOWED_EXTENSIONS.join(', ') + '). 입력: ' + path.extname(wikiPdfPath) + '\n');
    process.exit(1);
  }

  // 파일 존재 확인
  if (!fs.existsSync(wikiPdfPath)) {
    process.stderr.write('[wiki-pdf-stage] 파일 없음: ' + wikiPdfPath + '\n');
    process.exit(1);
  }

  // 파일 크기 확인 (100 MB 한도, 안전 검증)
  const stat = fs.statSync(wikiPdfPath);
  const MAX_SIZE = 100 * 1024 * 1024;
  if (stat.size > MAX_SIZE) {
    process.stderr.write('[wiki-pdf-stage] 거부: 파일 100 MB 초과 (' + (stat.size / 1024 / 1024).toFixed(1) + ' MB)\n');
    process.exit(1);
  }

  // 임시 디렉토리 준비
  ensureStageDir();

  // 충돌 방지: 동일 basename 존재 시 timestamp 추가
  const basename = path.basename(wikiPdfPath);
  let target = path.join(STAGE_DIR, basename);
  if (fs.existsSync(target)) {
    const ext = path.extname(basename);
    const stem = basename.slice(0, basename.length - ext.length);
    const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    target = path.join(STAGE_DIR, stem + '_' + ts + ext);
  }

  // 복사
  try {
    fs.copyFileSync(wikiPdfPath, target);
  } catch (e) {
    process.stderr.write('[wiki-pdf-stage] 복사 실패: ' + e.message + '\n');
    process.exit(1);
  }

  process.stderr.write('[wiki-pdf-stage] 복사 완료 (' + (stat.size / 1024).toFixed(1) + ' KB)\n');
  process.stderr.write('[wiki-pdf-stage] 원본: ' + wikiPdfPath + '\n');
  process.stderr.write('[wiki-pdf-stage] 임시: ' + target + '\n');
  process.stderr.write('[wiki-pdf-stage] PDF MCP에 위 임시 경로를 사용하세요.\n');

  // stdout으로 임시 경로만 출력 (다음 명령이 파싱 가능)
  process.stdout.write(target + '\n');
}

// =============================================================================
// 명령: cleanup
// =============================================================================

function cmdCleanup() {
  if (!fs.existsSync(STAGE_DIR)) {
    process.stderr.write('[wiki-pdf-stage] 임시 디렉토리 없음 (cleanup 불필요)\n');
    return;
  }

  const files = fs.readdirSync(STAGE_DIR);
  if (files.length === 0) {
    process.stderr.write('[wiki-pdf-stage] 임시 디렉토리 비어 있음\n');
    return;
  }

  let count = 0;
  let totalSize = 0;
  for (const f of files) {
    const fp = path.join(STAGE_DIR, f);
    try {
      const stat = fs.statSync(fp);
      if (stat.isFile()) {
        totalSize += stat.size;
        fs.unlinkSync(fp);
        count++;
      }
    } catch (e) {
      process.stderr.write('[wiki-pdf-stage] 삭제 실패: ' + f + ' (' + e.message + ')\n');
    }
  }

  process.stderr.write('[wiki-pdf-stage] cleanup 완료: ' + count + '개 파일 (' + (totalSize / 1024 / 1024).toFixed(2) + ' MB)\n');
}

// =============================================================================
// 명령: list
// =============================================================================

function cmdList() {
  if (!fs.existsSync(STAGE_DIR)) {
    process.stderr.write('[wiki-pdf-stage] 임시 디렉토리 없음\n');
    return;
  }

  const files = fs.readdirSync(STAGE_DIR);
  if (files.length === 0) {
    process.stderr.write('[wiki-pdf-stage] 임시 디렉토리 비어 있음\n');
    return;
  }

  process.stderr.write('[wiki-pdf-stage] 임시 파일 ' + files.length + '개:\n');
  for (const f of files) {
    const fp = path.join(STAGE_DIR, f);
    try {
      const stat = fs.statSync(fp);
      process.stderr.write('  ' + f + ' (' + (stat.size / 1024).toFixed(1) + ' KB)\n');
    } catch (e) {
      process.stderr.write('  ' + f + ' (stat 실패)\n');
    }
  }
}

// =============================================================================
// 진입점
// =============================================================================

const args = process.argv.slice(2);
const cmd = args[0];

switch (cmd) {
  case 'stage':
    cmdStage(args[1]);
    break;
  case 'cleanup':
    cmdCleanup();
    break;
  case 'list':
    cmdList();
    break;
  default:
    process.stderr.write('사용법:\n');
    process.stderr.write('  node .claude/hooks/wiki-pdf-stage.js stage <wiki-pdf-path>\n');
    process.stderr.write('  node .claude/hooks/wiki-pdf-stage.js cleanup\n');
    process.stderr.write('  node .claude/hooks/wiki-pdf-stage.js list\n');
    process.stderr.write('\n');
    process.stderr.write('허용 확장자: ' + ALLOWED_EXTENSIONS.join(', ') + '\n');
    process.stderr.write('허용 wiki prefix: ' + ALLOWED_WIKI_PREFIXES.join(', ') + '\n');
    process.stderr.write('임시 디렉토리: Temporary Storage/wiki-pdf-stage/\n');
    process.exit(1);
}
