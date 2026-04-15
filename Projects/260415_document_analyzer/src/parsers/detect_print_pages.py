"""인쇄 페이지 번호 자동 검출.

각 PDF 페이지의 하단 1/8 영역에서 텍스트 박스를 추출하고,
숫자만으로 구성된 짧은 토큰을 인쇄 페이지 후보로 식별한다.
연속 증가 검증으로 잡음 토큰을 걸러내고, 시퀀스 페이지(파일의 N번째)
와 인쇄 페이지의 매핑 테이블을 산출한다.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pdfplumber

sys.stdout.reconfigure(encoding="utf-8")

PROJECT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT / "Input" / "Source"
REFERENCE = PROJECT / "Input" / "Reference"
RUNTIME = PROJECT / ".bkit_runtime"
OUT = RUNTIME / "page_mapping.json"

INPUTS: dict[str, Path] = {
    "plan": SOURCE / "2026년 AID 전환 중점 전문대학 지원사업 사업계획서_순천제일대학교.pdf",
    "evidence": SOURCE / "2026년 AID 전환 중점 전문대학 지원사업 증빙자료_순천제일대학교.pdf",
    "pres": SOURCE / "AID 전환 중점 전문대학 지원사업 발표 자료(순천제일대+조선이공대).pdf",
    "indicator": REFERENCE / "평가지표.pdf",
    "format": REFERENCE / "붙임2. 2026년 AID 전환 중점 전문대학 지원사업 사업계획서 작성 서식.pdf",
}

PAGE_NUM_RE = re.compile(r"^[\-\.\s]*([0-9]{1,3})[\-\.\s]*$")


def _candidates_in_footer(page: pdfplumber.page.Page) -> list[int]:
    """페이지 하단 1/8 영역의 숫자만 토큰을 후보로 수집."""
    h = page.height
    cutoff = h * 7 / 8
    cands: list[int] = []
    try:
        words = page.extract_words(use_text_flow=False) or []
    except Exception:
        words = []
    for w in words:
        if w.get("top", 0) < cutoff:
            continue
        text = (w.get("text") or "").strip()
        m = PAGE_NUM_RE.match(text)
        if not m:
            continue
        try:
            n = int(m.group(1))
        except ValueError:
            continue
        if 0 <= n <= 999:
            cands.append(n)
    return cands


def _pick_print_number(cands: list[int],
                       prev_print: int | None) -> int | None:
    """후보 중 인쇄 번호를 선택. 직전+1 우선, 없으면 최빈/최소."""
    if not cands:
        return None
    if prev_print is not None:
        for c in cands:
            if c == prev_print + 1:
                return c
    counts: dict[int, int] = {}
    for c in cands:
        counts[c] = counts.get(c, 0) + 1
    return max(counts, key=lambda k: (counts[k], -k))


def detect(slug: str, pdf_path: Path) -> dict:
    if not pdf_path.exists():
        return {"slug": slug, "error": f"missing: {pdf_path}"}
    rows: list[dict] = []
    prev_print: int | None = None
    print_start_seq: int | None = None
    with pdfplumber.open(str(pdf_path)) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            cands = _candidates_in_footer(page)
            chosen = _pick_print_number(cands, prev_print)
            rows.append({
                "seq": idx,
                "print": chosen,
                "candidates": cands,
            })
            if chosen is not None:
                if print_start_seq is None and chosen == 1:
                    print_start_seq = idx
                prev_print = chosen
    detected_offset = (
        print_start_seq - 1 if print_start_seq is not None else None
    )
    return {
        "slug": slug,
        "pdf": str(pdf_path.name),
        "total_pages": len(rows),
        "print_start_seq": print_start_seq,
        "offset_seq_minus_print": detected_offset,
        "pages": rows,
    }


def main() -> None:
    out: dict[str, object] = {
        "schema": "page-mapping-v1",
        "method": "footer 1/8 region, numeric tokens, monotonic +1 preference",
        "documents": {},
    }
    for slug, path in INPUTS.items():
        print(f"[detect] {slug}: {path.name}")
        out["documents"][slug] = detect(slug, path)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"[OK] wrote {OUT}")
    for slug, info in out["documents"].items():
        if "error" in info:
            print(f"  {slug}: ERROR {info['error']}")
            continue
        ps = info.get("print_start_seq")
        off = info.get("offset_seq_minus_print")
        first_seq_with_print = next(
            (p["seq"] for p in info["pages"] if p["print"] is not None),
            None,
        )
        first_print = next(
            (p["print"] for p in info["pages"] if p["print"] is not None),
            None,
        )
        print(f"  {slug}: total={info['total_pages']}  "
              f"print_start_seq={ps}  offset={off}  "
              f"first_print={first_print}@seq{first_seq_with_print}")


if __name__ == "__main__":
    main()
