#!/usr/bin/env python3
"""
pdf-cite.py -- PDF 인용/레퍼런스 섹션 추출
Reference-Port: Graphify pdf pass 아이디어 — 우리는 기존 .txt 추출본 재사용 (50p+ AER-003 규칙)

입력: argv[1] = .txt (PDF 사전 추출본)
출력: stdout JSON { file, citations: [...], reference_count }
"""
import sys
import re
import json
from pathlib import Path


CITATION_PATTERNS = [
    re.compile(r"\[([A-Za-z][A-Za-z0-9 ,.&-]+?,\s*\d{4}[a-z]?)\]"),  # [Smith, 2020]
    re.compile(r"\(([A-Za-z][A-Za-z0-9 ,.&-]+?,\s*\d{4}[a-z]?)\)"),  # (Smith, 2020)
    re.compile(r"\bdoi:\s*(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE),
    re.compile(r"\barXiv:\s*(\d{4}\.\d{4,5})", re.IGNORECASE),
]


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: pdf-cite.py <txt>"}))
        sys.exit(1)
    p = Path(sys.argv[1])
    if not p.exists():
        print(json.dumps({"error": "file not found"}))
        sys.exit(1)
    text = p.read_text(encoding="utf-8", errors="replace")

    citations = []
    for pat in CITATION_PATTERNS:
        for m in pat.finditer(text):
            citations.append(m.group(1))
    # 중복 제거 순서 보존
    seen, uniq = set(), []
    for c in citations:
        if c not in seen:
            seen.add(c)
            uniq.append(c)

    print(json.dumps({
        "file": str(p),
        "citations": uniq[:200],
        "citation_count": len(uniq),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
