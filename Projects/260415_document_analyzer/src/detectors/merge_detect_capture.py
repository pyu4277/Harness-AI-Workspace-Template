"""Phase 3: detect merged-cell suspects, capture page PNGs.

OCR via tesseract eng (kor data not installed; Claude multimodal reads PNG in Phase 5).
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from pathlib import Path
from typing import Any

from pdf2image import convert_from_path

PROJECT = Path(__file__).resolve().parents[2]
RUNTIME = PROJECT / ".bkit_runtime"
TABLES_DIR = RUNTIME / "tables"
CAP_DIR = PROJECT / "Output" / "Reports" / "captures"

INPUTS: dict[str, Path] = {
    "plan": PROJECT / "Input" / "Source" / "2026년 AID 전환 중점 전문대학 지원사업 사업계획서_순천제일대학교.pdf",
    "evidence": PROJECT / "Input" / "Source" / "2026년 AID 전환 중점 전문대학 지원사업 증빙자료_순천제일대학교.pdf",
    "pres": PROJECT / "Input" / "Source" / "AID 전환 중점 전문대학 지원사업 발표 자료(순천제일대+조선이공대).pdf",
    "indicator": PROJECT / "Input" / "Reference" / "평가지표.pdf",
    "format": PROJECT / "Input" / "Reference" / "붙임2. 2026년 AID 전환 중점 전문대학 지원사업 사업계획서 작성 서식.pdf",
}

POPPLER_PATH = r"C:\Users\pyu42\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"

EMPTY_RATIO_THRESHOLD = 0.20
MIN_COMPLEX_COLS = 8


def _load_tables() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in sorted(TABLES_DIR.glob("*.json")):
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def _detect_signals(tbl: dict[str, Any]) -> dict[str, Any]:
    rows = tbl["rows"]
    n_rows = len(rows)
    n_cols = tbl["n_cols"]
    total = sum(len(r) for r in rows) or 1
    empty = sum(1 for r in rows for c in r if not c.strip())
    empty_ratio = round(empty / total, 4)
    col_counts = [len(r) for r in rows]
    col_stdev = round(statistics.pstdev(col_counts), 4) if col_counts else 0
    has_newlines = any("\n" in c for r in rows for c in r)

    signals = {
        "empty_ratio": empty_ratio,
        "empty_ratio_high": empty_ratio >= EMPTY_RATIO_THRESHOLD,
        "col_count_unstable": col_stdev > 0,
        "complex_cols": n_cols >= MIN_COMPLEX_COLS,
        "has_cell_newlines": has_newlines,
    }
    suspect = (
        signals["empty_ratio_high"]
        or signals["col_count_unstable"]
        or signals["complex_cols"]
    )
    return {
        "slug": tbl["slug"],
        "page": tbl["page"],
        "table_index": tbl["table_index"],
        "n_rows": n_rows,
        "n_cols": n_cols,
        "signals": signals,
        "suspect": suspect,
    }


def _capture_pages(slug: str, pdf_path: Path, pages: set[int]) -> dict[int, str]:
    if not pages:
        return {}
    print(f"  [CAP] {slug}: {len(pages)} pages → render", flush=True)
    sorted_pages = sorted(pages)
    out_paths: dict[int, str] = {}
    for p in sorted_pages:
        png = CAP_DIR / f"{slug}_p{p:04d}.png"
        if png.exists():
            out_paths[p] = png.name
            continue
        imgs = convert_from_path(
            str(pdf_path),
            dpi=200,
            first_page=p,
            last_page=p,
            poppler_path=POPPLER_PATH,
        )
        if imgs:
            imgs[0].save(str(png), "PNG", optimize=True)
            out_paths[p] = png.name
    return out_paths


def main() -> int:
    CAP_DIR.mkdir(parents=True, exist_ok=True)
    all_tables = _load_tables()
    print(f"[LOAD] {len(all_tables)} tables", flush=True)

    detected = [_detect_signals(t) for t in all_tables]
    suspects = [d for d in detected if d["suspect"]]
    print(f"[DETECT] suspect={len(suspects)}/{len(detected)}", flush=True)

    by_slug_pages: dict[str, set[int]] = {}
    for s in suspects:
        by_slug_pages.setdefault(s["slug"], set()).add(s["page"])

    capture_map: dict[str, dict[int, str]] = {}
    for slug, pages in by_slug_pages.items():
        capture_map[slug] = _capture_pages(slug, INPUTS[slug], pages)

    out = {
        "total_tables": len(detected),
        "suspect_count": len(suspects),
        "suspect_pages_per_slug": {k: sorted(list(v)) for k, v in by_slug_pages.items()},
        "captures": {k: list(v.values()) for k, v in capture_map.items()},
        "details": detected,
    }
    (RUNTIME / "suspect_tables.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[OK] suspect_tables.json + {sum(len(v) for v in capture_map.values())} PNGs", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
