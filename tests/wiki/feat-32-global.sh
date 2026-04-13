#!/usr/bin/env bash
set -e
python <<'PY'
import json, os
from pathlib import Path
reg = Path(os.path.expanduser("~")) / ".claude" / "wiki-registry.json"
assert reg.exists(), f"wiki-registry.json missing at {reg}"
d = json.loads(reg.read_text(encoding="utf-8"))
assert "projects" in d
assert any(p["id"] == "005_AI_Project" for p in d["projects"])
print(f"PASS feat-32 (wiki-registry.json: {len(d['projects'])} projects)")
PY
