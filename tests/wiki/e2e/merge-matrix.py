#!/usr/bin/env python
"""verification-matrix.md 에 E2E 컬럼 추가 (33 단위 + 6 시나리오 통합)."""
import sys, json, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
VM = ROOT.parent / "001_Wiki_AI/990_Meta/verification-matrix.md"
REPORTS = ROOT / "reports/e2e"

# E2E 시나리오에서 hit 한 feat 셋
hit_in = {f"{i:02d}": [] for i in range(1, 33)}
for s in ["s1","s2","s3","s4","s5","s6"]:
    p = REPORTS / f"{s}.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        for f in d.get("feats", []):
            try:
                f = f"{int(f):02d}"
                if f in hit_in:
                    hit_in[f].append(s)
            except ValueError:
                continue

text = VM.read_text(encoding="utf-8")
lines = text.splitlines()
out = []
in_table = False
header_written = False
for ln in lines:
    if ln.startswith("| Test ") and "Status" in ln:
        in_table = True
        if not header_written:
            out.append(ln.rstrip(" |") + " | E2E |")
            header_written = True
        continue
    if in_table and ln.startswith("|---"):
        out.append(ln.rstrip(" |") + "|------|")
        continue
    if in_table and ln.startswith("| ") and " feat-" in ln.split("|")[1]:
        name = ln.split("|")[1].strip()
        feat_num = name.split("-")[1] if name.startswith("feat-") else None
        scen = ",".join(hit_in.get(feat_num, [])) or "-"
        out.append(ln.rstrip(" |") + f" | {scen} |")
        continue
    if in_table and ln.startswith("| ") and "phase0" in ln:
        out.append(ln.rstrip(" |") + " | gate |")
        continue
    if in_table and not ln.startswith("|"):
        in_table = False
    out.append(ln)

VM.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"merged E2E column into {VM}")
print(f"covered: {sum(1 for v in hit_in.values() if v)}/32")
