"""Phase 4-1: extract heading anchors per page from all 5 PDFs.

Heading patterns:
  - Roman:  Ⅰ. Ⅱ. Ⅲ. Ⅳ. Ⅴ.
  - Numeric: 1.  1.1.  1.1.1.
  - Korean parens: 가. 나. 다. / (1) (2) / 1) 2)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PAGES_DIR = PROJECT / ".bkit_runtime" / "pages"
RUNTIME = PROJECT / ".bkit_runtime"

ROMAN = re.compile(r"^\s*([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ])\s*\.\s*(.{2,80}?)\s*$", re.MULTILINE)
NUM_DEEP = re.compile(r"^\s*(\d+)\.(\d+)(?:\.(\d+))?\s*\.?\s*(.{2,120}?)\s*$", re.MULTILINE)
NUM_TOP = re.compile(r"^\s*(\d{1,2})\.\s+([^\d\n].{2,100}?)\s*$", re.MULTILINE)


def extract_headings(text: str) -> list[dict]:
    found: list[dict] = []
    for m in ROMAN.finditer(text):
        found.append({"type": "roman", "code": m.group(1), "title": m.group(2).strip()})
    for m in NUM_DEEP.finditer(text):
        parts = [m.group(1), m.group(2)] + ([m.group(3)] if m.group(3) else [])
        code = ".".join(parts)
        found.append({"type": "deep", "code": code, "title": m.group(4).strip()})
    for m in NUM_TOP.finditer(text):
        # avoid double-matching with deep
        line = m.group(0)
        if "." in line.split(m.group(2))[0].strip()[:6]:
            continue
        if any(line.startswith(f"{m.group(1)}.{x}") for x in "0123456789"):
            continue
        found.append({"type": "top", "code": m.group(1) + ".", "title": m.group(2).strip()})
    return found


def main() -> int:
    out: dict[str, list] = {}
    for slug in ["plan", "evidence", "pres", "indicator", "format"]:
        pages = sorted(PAGES_DIR.glob(f"{slug}_p*.json"))
        slug_out = []
        for p in pages:
            d = json.loads(p.read_text(encoding="utf-8"))
            heads = extract_headings(d["text"])
            if heads:
                slug_out.append({"page": d["page"], "headings": heads, "preview": d["text"][:200]})
        out[slug] = slug_out
        print(f"[{slug}] pages_with_headings={len(slug_out)}", flush=True)

    (RUNTIME / "headings.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("[OK] headings.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
