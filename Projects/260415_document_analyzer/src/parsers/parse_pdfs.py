"""Phase 2 parser: 5 PDFs -> page JSON + table JSON.

Refer to refined MD Section 9 #3 (router) and AER-003 (50p threshold).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pdfplumber
from pypdf import PdfReader

PROJECT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT / "Input" / "Source"
REFERENCE = PROJECT / "Input" / "Reference"
RUNTIME = PROJECT / ".bkit_runtime"
PAGES_DIR = RUNTIME / "pages"
TABLES_DIR = RUNTIME / "tables"
TEXT_DIR = RUNTIME / "text"

INPUTS: dict[str, tuple[Path, str]] = {
    "plan": (SOURCE / "2026년 AID 전환 중점 전문대학 지원사업 사업계획서_순천제일대학교.pdf", "Source-Plan"),
    "evidence": (SOURCE / "2026년 AID 전환 중점 전문대학 지원사업 증빙자료_순천제일대학교.pdf", "Source-Evidence"),
    "pres": (SOURCE / "AID 전환 중점 전문대학 지원사업 발표 자료(순천제일대+조선이공대).pdf", "Source-Presentation"),
    "indicator": (REFERENCE / "평가지표.pdf", "Reference-Indicator"),
    "format": (REFERENCE / "붙임2. 2026년 AID 전환 중점 전문대학 지원사업 사업계획서 작성 서식.pdf", "Reference-Format"),
}

AER003_PAGE_THRESHOLD = 50


def _ensure_dirs() -> None:
    for d in (PAGES_DIR, TABLES_DIR, TEXT_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _page_count(pdf_path: Path) -> int:
    return len(PdfReader(str(pdf_path)).pages)


def _aer003_extract_text(slug: str, pdf_path: Path) -> Path:
    """Pre-extract full text via pdfplumber when page count > threshold."""
    out = TEXT_DIR / f"{slug}.txt"
    parts: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            t = page.extract_text() or ""
            parts.append(f"=== PAGE {i} ===\n{t}")
    out.write_text("\n\n".join(parts), encoding="utf-8")
    return out


def _parse_pdf(slug: str, pdf_path: Path, role: str) -> dict[str, Any]:
    pcount = _page_count(pdf_path)
    aer003_applied = pcount > AER003_PAGE_THRESHOLD
    if aer003_applied:
        _aer003_extract_text(slug, pdf_path)

    empty_pages = 0
    table_counts: list[int] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            if not text.strip():
                empty_pages += 1
            tables = page.extract_tables() or []
            page_obj = {
                "slug": slug,
                "role": role,
                "page": i,
                "text": text,
                "char_count": len(text),
                "table_count": len(tables),
                "bbox": list(page.bbox),
            }
            (PAGES_DIR / f"{slug}_p{i:04d}.json").write_text(
                json.dumps(page_obj, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            for j, tbl in enumerate(tables, 1):
                rows = [[("" if c is None else str(c)) for c in row] for row in tbl]
                tbl_obj = {
                    "slug": slug,
                    "role": role,
                    "page": i,
                    "table_index": j,
                    "n_rows": len(rows),
                    "n_cols": max((len(r) for r in rows), default=0),
                    "rows": rows,
                }
                (TABLES_DIR / f"{slug}_p{i:04d}_t{j:02d}.json").write_text(
                    json.dumps(tbl_obj, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            table_counts.append(len(tables))

    return {
        "slug": slug,
        "role": role,
        "file": pdf_path.name,
        "pages": pcount,
        "aer003_applied": aer003_applied,
        "empty_pages": empty_pages,
        "empty_ratio": round(empty_pages / pcount, 4) if pcount else 0,
        "tables_total": sum(table_counts),
        "pages_with_tables": sum(1 for c in table_counts if c > 0),
    }


def main() -> int:
    _ensure_dirs()
    summary: list[dict[str, Any]] = []
    for slug, (pdf_path, role) in INPUTS.items():
        if not pdf_path.exists():
            print(f"[MISSING] {slug}: {pdf_path}", file=sys.stderr)
            return 2
        print(f"[PARSE] {slug} ({role}) {pdf_path.name}", flush=True)
        s = _parse_pdf(slug, pdf_path, role)
        print(f"  pages={s['pages']} empty={s['empty_pages']} tables={s['tables_total']} aer003={s['aer003_applied']}", flush=True)
        summary.append(s)

    out = RUNTIME / "phase2_summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] summary -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
