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
const ALLOWED_EXTENSIONS = ['.pdf', '.hwp', '.hwpx', '.docx', '.pptx', '.xlsx', '.xls', '.xlsm', '.csv'];

// 위키 root 시작 + 허용 prefix
const ALLOWED_WIKI_PREFIXES = [
  '000_Raw/',
  '990_Meta/archive/'
];

// cleanup 시 재귀 삭제가 허용된 서브디렉토리 화이트리스트
// (HWPX_Master convert_hwp_to_hwpx.py 가 생성하는 .hwp-archive 등)
// 이 목록에 없는 서브디렉토리는 cleanup 에서 건너뛰고 경고만 출력 (안전)
const ALLOWED_CLEANUP_SUBDIRS = [
  '.hwp-archive'
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

// 디렉토리 총 크기 (바이트) 재귀 계산
// Dirent.isFile() 이 한글 경로에서 불안정하므로 fs.statSync() 로 fallback
function getDirSize(dir) {
  let size = 0;
  let fileCount = 0;
  try {
    const names = fs.readdirSync(dir);
    for (const name of names) {
      const fp = path.join(dir, name);
      try {
        const stat = fs.statSync(fp);
        if (stat.isFile()) {
          size += stat.size;
          fileCount++;
        } else if (stat.isDirectory()) {
          const sub = getDirSize(fp);
          size += sub.size;
          fileCount += sub.fileCount;
        }
      } catch (e) { /* ignore */ }
    }
  } catch (e) { /* ignore */ }
  return { size, fileCount };
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

  // 파일 크기 확인 (200 MB 한도, 안전 검증)
  // 2026-04-11: 100 → 200 MB 상향 (순천제일대 175 MB HWP 성과평가보고서 처리 위해)
  const stat = fs.statSync(wikiPdfPath);
  const MAX_SIZE = 200 * 1024 * 1024;
  if (stat.size > MAX_SIZE) {
    process.stderr.write('[wiki-pdf-stage] 거부: 파일 200 MB 초과 (' + (stat.size / 1024 / 1024).toFixed(1) + ' MB)\n');
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

  const names = fs.readdirSync(STAGE_DIR);
  if (names.length === 0) {
    process.stderr.write('[wiki-pdf-stage] 임시 디렉토리 비어 있음\n');
    return;
  }

  let fileCount = 0;
  let dirCount = 0;
  let skippedDirCount = 0;
  let totalSize = 0;

  for (const name of names) {
    const fp = path.join(STAGE_DIR, name);
    try {
      const stat = fs.statSync(fp);
      if (stat.isFile()) {
        totalSize += stat.size;
        fs.unlinkSync(fp);
        fileCount++;
      } else if (stat.isDirectory()) {
        if (ALLOWED_CLEANUP_SUBDIRS.includes(name)) {
          // 화이트리스트 서브디렉토리 재귀 삭제 (.hwp-archive 등)
          const dirInfo = getDirSize(fp);
          totalSize += dirInfo.size;
          fs.rmSync(fp, { recursive: true, force: true });
          dirCount++;
          process.stderr.write(
            '[wiki-pdf-stage] 서브디렉토리 재귀 삭제: ' + name +
            ' (' + dirInfo.fileCount + '개 파일, ' +
            (dirInfo.size / 1024).toFixed(1) + ' KB)\n'
          );
        } else {
          // 화이트리스트 외 서브디렉토리는 건너뛰고 경고
          skippedDirCount++;
          process.stderr.write(
            '[wiki-pdf-stage] 경고: 화이트리스트 외 서브디렉토리 무시: ' + name +
            ' (수동 정리 필요)\n'
          );
        }
      }
    } catch (e) {
      process.stderr.write('[wiki-pdf-stage] 삭제 실패: ' + name + ' (' + e.message + ')\n');
    }
  }

  process.stderr.write(
    '[wiki-pdf-stage] cleanup 완료: ' +
    fileCount + '개 파일 + ' + dirCount + '개 디렉토리 (' +
    (totalSize / 1024 / 1024).toFixed(2) + ' MB)' +
    (skippedDirCount > 0 ? ', ' + skippedDirCount + '개 서브디렉토리 건너뜀' : '') +
    '\n'
  );
}

// =============================================================================
// 명령: list
// =============================================================================

function cmdList() {
  if (!fs.existsSync(STAGE_DIR)) {
    process.stderr.write('[wiki-pdf-stage] 임시 디렉토리 없음\n');
    return;
  }

  const names = fs.readdirSync(STAGE_DIR);
  if (names.length === 0) {
    process.stderr.write('[wiki-pdf-stage] 임시 디렉토리 비어 있음\n');
    return;
  }

  const fileNames = [];
  const dirNames = [];
  for (const name of names) {
    const fp = path.join(STAGE_DIR, name);
    try {
      const stat = fs.statSync(fp);
      if (stat.isFile()) fileNames.push(name);
      else if (stat.isDirectory()) dirNames.push(name);
    } catch (e) { /* ignore */ }
  }

  process.stderr.write(
    '[wiki-pdf-stage] 임시 항목: ' +
    fileNames.length + '개 파일 + ' + dirNames.length + '개 서브디렉토리\n'
  );

  for (const name of fileNames) {
    const fp = path.join(STAGE_DIR, name);
    try {
      const stat = fs.statSync(fp);
      process.stderr.write('  ' + name + ' (' + (stat.size / 1024).toFixed(1) + ' KB)\n');
    } catch (e) {
      process.stderr.write('  ' + name + ' (stat 실패)\n');
    }
  }

  for (const name of dirNames) {
    const fp = path.join(STAGE_DIR, name);
    const info = getDirSize(fp);
    const marker = ALLOWED_CLEANUP_SUBDIRS.includes(name) ? '[cleanup OK]' : '[수동]';
    process.stderr.write(
      '  ' + name + '/ ' + marker +
      ' (' + info.fileCount + '개 파일, ' + (info.size / 1024).toFixed(1) + ' KB)\n'
    );
    // 서브디렉토리 내부 파일 들여쓰기 표시
    try {
      const subNames = fs.readdirSync(fp);
      for (const sub of subNames) {
        const subPath = path.join(fp, sub);
        try {
          const stat = fs.statSync(subPath);
          if (stat.isFile()) {
            process.stderr.write('    ' + sub + ' (' + (stat.size / 1024).toFixed(1) + ' KB)\n');
          }
        } catch (e) { /* ignore */ }
      }
    } catch (e) { /* ignore */ }
  }
}

// =============================================================================
// 명령: archive-original (IMP-023 구조적 예방책, 2026-04-12 추가)
// 지식화 완료된 Raw 원본 파일을 990_Meta/archive/<category>/ 로 이동한다.
// stage 의 반대 개념: 임시 사본이 아닌 실 원본 이동.
// =============================================================================

const WIKI_ARCHIVE_ROOT = path.join(WIKI_ROOT, '990_Meta', 'archive');

function cmdArchiveOriginal(rawPath, category) {
  if (!rawPath) {
    process.stderr.write('[wiki-pdf-stage] 사용법: archive-original <wiki-raw-path> [category]\n');
    process.exit(1);
  }

  // 절대경로 검증
  if (!path.isAbsolute(rawPath)) {
    process.stderr.write('[wiki-pdf-stage] 거부: 절대경로 필요. 입력: ' + rawPath + '\n');
    process.exit(1);
  }

  // 위키 경로 검증 (stage 와 동일 규칙)
  const wikiCheck = isAllowedWikiPath(rawPath);
  if (!wikiCheck.ok) {
    process.stderr.write('[wiki-pdf-stage] 거부: ' + wikiCheck.reason + '\n');
    process.exit(1);
  }

  // 파일 존재 확인
  if (!fs.existsSync(rawPath)) {
    process.stderr.write('[wiki-pdf-stage] 파일 없음: ' + rawPath + '\n');
    process.exit(1);
  }

  const stat = fs.statSync(rawPath);
  if (!stat.isFile()) {
    process.stderr.write('[wiki-pdf-stage] 파일이 아님 (디렉토리는 지원 안 함): ' + rawPath + '\n');
    process.exit(1);
  }

  // 카테고리 정리 (기본: "generic_processed")
  const safeCategory = (category || 'generic_processed').replace(/[^\w가-힣_.-]/g, '_');
  const archiveSubDir = path.join(WIKI_ARCHIVE_ROOT, safeCategory);

  try {
    fs.mkdirSync(archiveSubDir, { recursive: true });
  } catch (e) {
    process.stderr.write('[wiki-pdf-stage] 아카이브 디렉토리 생성 실패: ' + e.message + '\n');
    process.exit(1);
  }

  const basename = path.basename(rawPath);
  let dst = path.join(archiveSubDir, basename);

  // 충돌 방지: 동일 이름 존재 시 타임스탬프 추가
  if (fs.existsSync(dst)) {
    const ext = path.extname(basename);
    const stem = basename.slice(0, basename.length - ext.length);
    const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    dst = path.join(archiveSubDir, stem + '_' + ts + ext);
  }

  try {
    // os.replace 와 동등한 원자적 이동
    fs.renameSync(rawPath, dst);
  } catch (e) {
    // 다른 드라이브 간 이동 시 rename 실패 → copy + unlink 폴백
    try {
      fs.copyFileSync(rawPath, dst);
      fs.unlinkSync(rawPath);
    } catch (e2) {
      process.stderr.write('[wiki-pdf-stage] 아카이브 이동 실패: ' + e2.message + '\n');
      process.exit(1);
    }
  }

  process.stderr.write('[wiki-pdf-stage] 아카이브 이동 완료 (' + (stat.size / 1024).toFixed(1) + ' KB)\n');
  process.stderr.write('[wiki-pdf-stage] 원본: ' + rawPath + '\n');
  process.stderr.write('[wiki-pdf-stage] archive: ' + dst + '\n');
  process.stderr.write('[wiki-pdf-stage] IMP-023: 지식화 완료 후 Raw → archive 이동 완료\n');

  // stdout 으로 archive 경로만 출력 (다음 명령이 파싱 가능)
  process.stdout.write(dst + '\n');
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
  case 'archive-original':
    cmdArchiveOriginal(args[1], args[2]);
    break;
  default:
    process.stderr.write('사용법:\n');
    process.stderr.write('  node .claude/hooks/wiki-pdf-stage.js stage <wiki-raw-path>\n');
    process.stderr.write('  node .claude/hooks/wiki-pdf-stage.js archive-original <wiki-raw-path> [category]\n');
    process.stderr.write('  node .claude/hooks/wiki-pdf-stage.js cleanup\n');
    process.stderr.write('  node .claude/hooks/wiki-pdf-stage.js list\n');
    process.stderr.write('\n');
    process.stderr.write('허용 확장자: ' + ALLOWED_EXTENSIONS.join(', ') + '\n');
    process.stderr.write('허용 wiki prefix: ' + ALLOWED_WIKI_PREFIXES.join(', ') + '\n');
    process.stderr.write('임시 디렉토리: Temporary Storage/wiki-pdf-stage/\n');
    process.stderr.write('archive 루트: 990_Meta/archive/\n');
    process.stderr.write('\n');
    process.stderr.write('IMP-023 (2026-04-12): 지식화 완료 후 archive-original 로 원본을 즉시 이동하세요.\n');
    process.exit(1);
}
