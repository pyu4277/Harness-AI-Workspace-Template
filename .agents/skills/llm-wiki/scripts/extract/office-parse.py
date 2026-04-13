#!/usr/bin/env python3
"""
office-parse.py -- Office 문서 (docx/pptx/xlsx/hwpx) 텍스트 추출
Reference-Port: 통합 제품 미사용. docx/pptx는 표준 zip + xml, hwpx 동일 zip 구조.
"""
import sys
import json
import zipfile
import re
from pathlib import Path


def extract_xml_text(zf, name_filter):
    collected = []
    for name in zf.namelist():
        if name_filter(name):
            try:
                xml = zf.read(name).decode("utf-8", errors="replace")
                text = re.sub(r"<[^>]+>", " ", xml)
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    collected.append(text)
            except Exception:
                continue
    return "\n".join(collected)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: office-parse.py <file>"}))
        sys.exit(1)
    p = Path(sys.argv[1])
    if not p.exists():
        print(json.dumps({"error": "file not found"}))
        sys.exit(1)

    suf = p.suffix.lower()
    text = ""
    kind = "unknown"
    try:
        with zipfile.ZipFile(p) as zf:
            if suf == ".docx":
                kind = "docx"
                text = extract_xml_text(zf, lambda n: n == "word/document.xml")
            elif suf == ".pptx":
                kind = "pptx"
                text = extract_xml_text(zf, lambda n: n.startswith("ppt/slides/slide"))
            elif suf == ".xlsx":
                kind = "xlsx"
                text = extract_xml_text(zf, lambda n: n.startswith("xl/sharedStrings") or n.startswith("xl/worksheets/sheet"))
            elif suf == ".hwpx":
                kind = "hwpx"
                text = extract_xml_text(zf, lambda n: n.startswith("Contents/section") and n.endswith(".xml"))
            else:
                print(json.dumps({"error": "unsupported", "suffix": suf}))
                sys.exit(1)
    except zipfile.BadZipFile:
        print(json.dumps({"error": "not a zip-based office file"}))
        sys.exit(1)

    print(json.dumps({
        "file": str(p),
        "kind": kind,
        "text_length": len(text),
        "text_excerpt": text[:500],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
