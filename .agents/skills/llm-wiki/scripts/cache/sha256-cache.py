#!/usr/bin/env python3
"""
sha256-cache.py -- 파일 내용 기반 캐시로 중복 ingest 방지
Reference-Port: MindVault cache hit 아이디어

입력: argv[1] = check|put, argv[2] = 파일 경로
출력: stdout JSON { hit: bool, hash, cached_at? }
캐시: .harness/ingest-cache.json
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


CACHE = Path.cwd() / ".harness" / "ingest-cache.json"


def load():
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save(d):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "usage: sha256-cache.py check|put <file>"}))
        sys.exit(1)
    mode = sys.argv[1]
    p = Path(sys.argv[2])
    if not p.exists():
        print(json.dumps({"error": "file not found"}))
        sys.exit(1)

    h = sha256_of(p)
    db = load()
    key = str(p.resolve())

    if mode == "check":
        entry = db.get(key)
        hit = bool(entry and entry.get("hash") == h)
        print(json.dumps({"hit": hit, "hash": h,
                          "cached_at": entry.get("cached_at") if entry else None}))
    elif mode == "put":
        db[key] = {"hash": h, "cached_at": datetime.now(timezone.utc).isoformat()}
        save(db)
        print(json.dumps({"stored": True, "hash": h}))
    else:
        print(json.dumps({"error": f"unknown mode: {mode}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
