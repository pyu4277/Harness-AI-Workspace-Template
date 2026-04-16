"""
Markdown -> HWPX 정밀 변환 (2-Phase, ADR-VA-005 패턴)

Phase 1: python-hwpx 로 텍스트 + 표 + 이미지 마커 작성
Phase 2: 한/글 COM 으로 마커를 실제 PNG 로 교체
사이드 작업: ```mermaid``` 블록을 mmdc 로 PNG 렌더 (npx 캐시 사용)

본문 폭 150mm = 567px (96 DPI) -- 260414_VideoAnalyzer ADR-VA-006 차용
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import hwpx

sys.stdout.reconfigure(encoding="utf-8")

STYLE_BODY = 1
STYLE_H1 = 2
STYLE_H2 = 3
STYLE_H3 = 4
STYLE_CAPTION = 22

IMG_MARKER_FMT = "<<IMG:{name}>>"
BODY_WIDTH_PX = 567  # 150mm @ 96 DPI

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
FENCE_RE = re.compile(r"^```(\w*)\s*$")
TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|?\s*$")


@dataclass
class Block:
    kind: str  # heading | paragraph | table | image_marker
    payload: object


@dataclass
class MermaidImage:
    marker_name: str
    png_path: Path


def parse_markdown(md_text: str, mmd_dir: Path, png_dir: Path,
                   slug: str) -> list[Block]:
    """MD 텍스트 -> Block 리스트. ```mermaid``` 는 PNG 렌더 후 이미지 마커로 치환."""
    blocks: list[Block] = []
    table_buf: list[str] = []
    in_fence = False
    fence_lang = ""
    fence_buf: list[str] = []
    mermaid_idx = 0

    def flush_table() -> None:
        nonlocal table_buf
        if table_buf:
            rows = _parse_md_table(table_buf)
            if rows:
                blocks.append(Block("table", rows))
            table_buf = []

    for raw in md_text.splitlines():
        line = raw.rstrip()

        if in_fence:
            m = FENCE_RE.match(line)
            if m:
                in_fence = False
                if fence_lang.lower() == "mermaid":
                    name = f"{slug}_mmd_{mermaid_idx:02d}"
                    mermaid_idx += 1
                    png_path = _render_mermaid(
                        "\n".join(fence_buf), name, mmd_dir, png_dir,
                    )
                    if png_path is not None:
                        blocks.append(Block("image_marker",
                                            MermaidImage(name, png_path)))
                else:
                    # 일반 코드블록은 paragraph 로 처리 (등폭 표시 손실 감수)
                    for fb in fence_buf:
                        blocks.append(Block("paragraph", fb))
                fence_buf = []
                fence_lang = ""
            else:
                fence_buf.append(line)
            continue

        m = FENCE_RE.match(line)
        if m:
            flush_table()
            in_fence = True
            fence_lang = m.group(1)
            fence_buf = []
            continue

        m = HEADING_RE.match(line)
        if m:
            flush_table()
            blocks.append(Block("heading",
                                (len(m.group(1)), m.group(2).strip())))
            continue

        if "|" in line and line.lstrip().startswith("|"):
            table_buf.append(line)
            continue

        flush_table()
        text = line.strip()
        if text:
            blocks.append(Block("paragraph", text))

    flush_table()
    return blocks


def _parse_md_table(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        s = line.strip()
        if not s or TABLE_SEP_RE.match(s):
            continue
        cells = [c.strip() for c in s.split("|")]
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if cells:
            rows.append(cells)
    return rows


def _render_mermaid(source: str, name: str, mmd_dir: Path,
                    png_dir: Path) -> Path | None:
    """mmdc 로 mermaid -> PNG. 동일 해시면 캐시 재사용."""
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:10]
    fname = f"{name}_{digest}.png"
    out = png_dir / fname
    if out.exists():
        return out
    mmd_path = mmd_dir / f"{name}_{digest}.mmd"
    mmd_path.write_text(source, encoding="utf-8")
    cmd = [
        "npx", "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc",
        "-i", str(mmd_path), "-o", str(out),
        "-b", "white", "-w", "1400",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, errors="replace",
            shell=True,
        )
    except OSError as exc:
        print(f"[mmdc] OSError {name}: {exc}", file=sys.stderr)
        return None
    if proc.returncode != 0 or not out.exists():
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-3:]
        print(f"[mmdc FAIL] {name}: {' | '.join(tail)}", file=sys.stderr)
        return None
    return out


def write_phase1(blocks: list[Block], hwpx_path: Path,
                 title: str) -> list[MermaidImage]:
    """python-hwpx 로 텍스트 + 표 + 이미지 마커 HWPX 작성. 마커 목록 반환."""
    doc = hwpx.HwpxDocument.new()
    doc.add_paragraph(title, style_id_ref=STYLE_H1)
    doc.add_paragraph("", style_id_ref=STYLE_BODY)

    images: list[MermaidImage] = []
    for blk in blocks:
        if blk.kind == "heading":
            level, text = blk.payload  # type: ignore[misc]
            style = {1: STYLE_H1, 2: STYLE_H2, 3: STYLE_H3}.get(
                level, STYLE_H3,
            )
            doc.add_paragraph(text, style_id_ref=style)
        elif blk.kind == "paragraph":
            doc.add_paragraph(str(blk.payload), style_id_ref=STYLE_BODY)
        elif blk.kind == "table":
            rows: list[list[str]] = blk.payload  # type: ignore[assignment]
            if not rows:
                continue
            n_rows = len(rows)
            n_cols = max(len(r) for r in rows)
            tbl = doc.add_table(n_rows, n_cols)
            for r, row in enumerate(rows):
                for c, cell in enumerate(row):
                    if c < n_cols:
                        tbl.set_cell_text(r, c, str(cell))
            doc.add_paragraph("", style_id_ref=STYLE_BODY)
        elif blk.kind == "image_marker":
            mi: MermaidImage = blk.payload  # type: ignore[assignment]
            doc.add_paragraph(IMG_MARKER_FMT.format(name=mi.marker_name),
                              style_id_ref=STYLE_BODY)
            doc.add_paragraph(f"[그림] {mi.marker_name}",
                              style_id_ref=STYLE_CAPTION)
            images.append(mi)

    doc.save_to_path(str(hwpx_path))
    return images


def phase2_insert_images(hwpx_path: Path,
                         images: list[MermaidImage]) -> int:
    """한/글 COM 으로 마커를 실제 이미지로 교체."""
    if not images:
        return 0
    import win32com.client as win32  # type: ignore[import-not-found]

    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FileCheck")
    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except Exception:
        pass

    inserted = 0
    try:
        hwp.Open(str(hwpx_path.resolve()))
        for mi in images:
            marker = IMG_MARKER_FMT.format(name=mi.marker_name)
            hwp.MovePos(2)  # moveBOF
            pset = hwp.HParameterSet.HFindReplace
            hwp.HAction.GetDefault("RepeatFind", pset.HSet)
            pset.FindString = marker
            pset.Direction = 0
            pset.IgnoreMessage = 1
            if not hwp.HAction.Execute("RepeatFind", pset.HSet):
                print(f"  [skip] marker not found: {mi.marker_name}",
                      file=sys.stderr)
                continue
            hwp.HAction.Run("Cancel")
            for _ in range(len(marker)):
                hwp.HAction.Run("MoveLeft")
            for _ in range(len(marker)):
                hwp.HAction.Run("MoveSelRight")
            hwp.HAction.Run("Delete")
            ctrl = hwp.InsertPicture(
                str(mi.png_path.resolve()), True, 2, False, False, 0,
            )
            if ctrl is not None:
                inserted += 1
        hwp.SaveAs(str(hwpx_path.resolve()), "HWPX")
    finally:
        try:
            hwp.Quit()
        except Exception:
            pass
    return inserted


def convert(md_path: Path, hwpx_path: Path, mmd_dir: Path,
            png_dir: Path) -> tuple[int, int]:
    md_text = md_path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else md_path.stem
    slug = md_path.stem
    blocks = parse_markdown(md_text, mmd_dir, png_dir, slug)
    images = write_phase1(blocks, hwpx_path, title)
    inserted = phase2_insert_images(hwpx_path, images)
    return len(images), inserted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True, help="입력 .md (또는 디렉토리)")
    ap.add_argument("--out", required=True, help="출력 .hwpx (또는 디렉토리)")
    ap.add_argument("--mmd-dir", required=True)
    ap.add_argument("--png-dir", required=True)
    args = ap.parse_args()

    mmd_dir = Path(args.mmd_dir)
    png_dir = Path(args.png_dir)
    mmd_dir.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)

    md_arg = Path(args.md)
    out_arg = Path(args.out)
    if md_arg.is_dir():
        out_arg.mkdir(parents=True, exist_ok=True)
        targets = sorted(md_arg.glob("*.md"))
        for md in targets:
            hwpx_path = out_arg / f"{md.stem}.hwpx"
            n_img, n_ins = convert(md, hwpx_path, mmd_dir, png_dir)
            print(f"[OK] {md.name} -> {hwpx_path.name}  "
                  f"(images: {n_ins}/{n_img})")
    else:
        n_img, n_ins = convert(md_arg, out_arg, mmd_dir, png_dir)
        print(f"[OK] {md_arg.name} -> {out_arg.name}  "
              f"(images: {n_ins}/{n_img})")


if __name__ == "__main__":
    main()
