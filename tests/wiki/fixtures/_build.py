"""Generate all binary fixtures (pdf/wav/png/docx/pptx). Idempotent."""
import sys, os, zipfile, struct, zlib, wave
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).parent

def write(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"  +{path.relative_to(ROOT)} ({len(data)}b)")

# 1. PDF (minimal valid 1-page text PDF)
def build_pdf():
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length 120 >>\nstream\nBT /F1 14 Tf 50 720 Td (Karpathy LLM 101 sample) Tj 0 -20 Td ([Smith, 2020] cited) Tj 0 -20 Td (doi:10.1234/example) Tj ET\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for o in offs:
        out += f"{o:010d} 00000 n \n".encode()
    out += f"trailer << /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    write(ROOT/"pdf/karpathy-llm101.pdf", bytes(out))

# 2. WAV (30s silence, 8kHz mono)
def build_wav():
    out = ROOT/"audio/short-30s.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(b"\x00\x00" * 8000 * 30)
    print(f"  +audio/short-30s.wav ({out.stat().st_size}b)")
    write(ROOT/"audio/short-30s.expected.txt", b"(silence -- whisper graceful skip)\n")

# 3. PNG (1x1 transparent)
def build_png():
    sig = b"\x89PNG\r\n\x1a\n"
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t+d) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00\x00\x00\x00")
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    write(ROOT/"image/chart-flow.png", png)
    write(ROOT/"image/chart-flow.caption.txt", "Flow chart: ingest -> graph -> bm25 -> mcp\n".encode("utf-8"))

# 4. docx / pptx (minimal valid OOXML)
def build_docx():
    out = ROOT/"office/notes.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    body = '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>E2E test note for office parser. transformer attention.</w:t></w:r></w:p></w:body></w:document>'
    rels = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    ct = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", body)
    print(f"  +office/notes.docx ({out.stat().st_size}b)")

def build_pptx():
    out = ROOT/"office/notes.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    slide = '<?xml version="1.0"?><p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>BM25 layered retrieval</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'
    ct = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>'
    rels = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/slides/slide1.xml"/></Relationships>'
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("ppt/slides/slide1.xml", slide)
    print(f"  +office/notes.pptx ({out.stat().st_size}b)")

if __name__ == "__main__":
    print("Building binary fixtures...")
    build_pdf(); build_wav(); build_png(); build_docx(); build_pptx()
    print("OK")
