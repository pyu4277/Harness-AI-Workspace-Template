#!/usr/bin/env python
"""32 feat × 6 scenario 매트릭스 + e2e-matrix.md 생성."""
import sys, json, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports/e2e"
MATRIX_OUT = ROOT.parent / "001_Wiki_AI/990_Meta/e2e-matrix.md"

SCEN = ["s1","s2","s3","s4","s5","s6"]
FEATS = [f"{i:02d}" for i in range(1, 33)]

# 1. 시나리오 보고서 적재
data = {}
for s in SCEN:
    f = REPORTS / f"{s}.json"
    if not f.exists():
        data[s] = {"id": s, "status": "MISSING", "feats": [], "elapsed_s": 0}
    else:
        data[s] = json.loads(f.read_text(encoding="utf-8"))

# 2. 커버리지 계산
hits = {f: [] for f in FEATS}
for s, d in data.items():
    for ft in d.get("feats", []):
        ft = f"{int(ft):02d}"
        if ft in hits:
            hits[ft].append(s)

zero_hit = [f for f, ss in hits.items() if not ss]
multi_hit = sum(1 for ss in hits.values() if len(ss) > 1)

# 3. 매트릭스 markdown
MATRIX_OUT.parent.mkdir(parents=True, exist_ok=True)
out = []
out.append("---")
out.append('title: "LLM Wiki E2E 매트릭스"')
out.append("type: analysis")
out.append("domain: 990_Meta")
out.append("schema_version: 2")
out.append(f"created: {datetime.datetime.now().isoformat()}")
out.append("---")
out.append("")
out.append("# LLM Wiki E2E 매트릭스 (PDCA 자동생성)")
out.append("")
out.append(f"- 시나리오: {len(SCEN)}")
out.append(f"- 통과: {sum(1 for d in data.values() if d.get('status')=='PASS')}/{len(SCEN)}")
out.append(f"- 32 기능 커버리지: {32-len(zero_hit)}/32 (0-hit: {len(zero_hit)}, 다중 hit: {multi_hit})")
out.append("")
out.append("## 시나리오 결과")
out.append("")
out.append("| ID | Name | Status | Elapsed | Feats hit |")
out.append("|----|------|--------|---------|-----------|")
for s in SCEN:
    d = data[s]
    out.append(f"| {s} | {d.get('name','-')} | {d.get('status','-')} | {d.get('elapsed_s',0)}s | {','.join(sorted(set(d.get('feats',[]))))} |")
out.append("")
out.append("## 32 기능 × 시나리오 그리드")
out.append("")
out.append("| Feat | " + " | ".join(SCEN) + " | Hit |")
out.append("|------|" + "|".join(["----"]*len(SCEN)) + "|-----|")
for f in FEATS:
    row = [f]
    for s in SCEN:
        row.append("O" if s in hits[f] else " ")
    row.append(str(len(hits[f])))
    out.append("| " + " | ".join(row) + " |")
out.append("")
if zero_hit:
    out.append(f"## 0-hit 기능 ({len(zero_hit)}건)")
    out.append("")
    out.append(", ".join(zero_hit))
    out.append("")

MATRIX_OUT.write_text("\n".join(out), encoding="utf-8")
print(f"matrix -> {MATRIX_OUT}")
print(f"coverage: {32-len(zero_hit)}/32 (zero-hit: {len(zero_hit)})")
if zero_hit:
    print(f"zero_hit: {zero_hit}")
