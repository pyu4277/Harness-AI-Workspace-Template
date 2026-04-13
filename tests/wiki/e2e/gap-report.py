#!/usr/bin/env python
"""0-hit 기능 + FAIL 시나리오 -> IMP 후보 추출."""
import sys, json, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports/e2e"
GAP_OUT = ROOT.parent / "001_Wiki_AI/990_Meta/e2e-gap-report.md"

SCEN = ["s1","s2","s3","s4","s5","s6"]
FEATS = [f"{i:02d}" for i in range(1, 33)]

data = {}
for s in SCEN:
    f = REPORTS / f"{s}.json"
    if f.exists():
        data[s] = json.loads(f.read_text(encoding="utf-8"))
    else:
        data[s] = {"status": "MISSING", "feats": []}

hits = {f: [] for f in FEATS}
for s, d in data.items():
    for ft in d.get("feats", []):
        ft = f"{int(ft):02d}"
        if ft in hits:
            hits[ft].append(s)

zero_hit = [f for f, ss in hits.items() if not ss]
failed = [s for s, d in data.items() if d.get("status") not in ("PASS",)]

GAP_OUT.parent.mkdir(parents=True, exist_ok=True)
out = ["---", 'title: "LLM Wiki E2E 갭 리포트"', "type: analysis", "domain: 990_Meta",
       "schema_version: 2", f"created: {datetime.datetime.now().isoformat()}", "---", "",
       "# E2E PDCA 갭 리포트", "",
       f"- 0-hit 기능: {len(zero_hit)}",
       f"- FAIL/MISSING 시나리오: {len(failed)}", ""]

if zero_hit:
    out.append("## 0-hit 기능 (IMP 후보)")
    out.append("")
    for f in zero_hit:
        out.append(f"- feat-{f}: 시나리오 미커버 -> 신규 시나리오/단위테스트 강화 권고")
    out.append("")

if failed:
    out.append("## FAIL/MISSING 시나리오")
    out.append("")
    for s in failed:
        d = data[s]
        out.append(f"- {s} ({d.get('status')}): {d.get('name','-')}")
    out.append("")

if not zero_hit and not failed:
    out.append("## 결과")
    out.append("")
    out.append("**전 기능 커버 + 전 시나리오 PASS** -- 자동발행 IMP 없음.")
    out.append("")

GAP_OUT.write_text("\n".join(out), encoding="utf-8")
print(f"gap report -> {GAP_OUT}")
print(f"zero_hit={len(zero_hit)} failed_scenarios={len(failed)}")
