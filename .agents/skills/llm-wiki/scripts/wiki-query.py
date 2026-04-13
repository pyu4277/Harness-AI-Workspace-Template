#!/usr/bin/env python3
"""
wiki-query.py -- BM25 기반 3-layer 토큰 예산 쿼리 엔진
Reference-Port: MindVault "0/100/800 token budget" 수치만 차용 (구현은 자체)

사용:
  python wiki-query.py "query text" [--layer 0|100|800]
출력: stdout JSON { query, layer, budget, results: [...], token_estimate }

layer 의미:
  0   — 링크 리스트만 (최저비용)
  100 — frontmatter + 한 줄 요약
  800 — 본문 포함 발췌 (최대 800 토큰 근사)
"""
import sys
import os
import re
import json
import argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def find_wiki_root():
    env = os.environ.get("WIKI_ROOT")
    if env:
        return Path(env).resolve()
    return (Path.cwd().parent / "001_Wiki_AI").resolve()


def tokenize(text: str):
    return [t for t in re.split(r"[^\w]+", text.lower()) if len(t) >= 2]


def iter_pages(root: Path):
    for md in root.rglob("*.md"):
        rel = md.relative_to(root).as_posix()
        top = rel.split("/", 1)[0] if "/" in rel else ""
        if top in ("000_Raw", "Clippings", ".obsidian") or "archive" in rel:
            continue
        yield md, rel


def extract_frontmatter(text: str):
    m = re.match(r"^---\n([\s\S]*?)\n---\n?", text)
    fm = m.group(1) if m else ""
    body = text[m.end():] if m else text
    title_m = re.search(r"^title:\s*\"?([^\"\n]+)\"?", fm, re.M)
    title = title_m.group(1).strip() if title_m else ""
    return title, fm, body


def approx_tokens(text: str) -> int:
    # 한/영 혼용 근사: 4자 = 1 token
    return max(1, len(text) // 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--layer", type=int, choices=[0, 100, 800], default=100)
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args()

    root = find_wiki_root()
    if not root.exists():
        print(json.dumps({"error": f"WIKI_ROOT not found: {root}"}))
        sys.exit(1)

    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        print(json.dumps({"error": "rank_bm25 not installed"}))
        sys.exit(1)

    corpus = []
    meta = []
    for md, rel in iter_pages(root):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        title, fm, body = extract_frontmatter(text)
        tokens = tokenize(title + " " + body)
        if not tokens:
            continue
        corpus.append(tokens)
        meta.append({"rel": rel, "title": title, "fm": fm, "body": body})

    if not corpus:
        print(json.dumps({"query": args.query, "layer": args.layer, "results": [],
                          "error": "empty corpus"}))
        return

    bm25 = BM25Okapi(corpus)
    q_tokens = tokenize(args.query)
    scores = bm25.get_scores(q_tokens)
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:args.top_k]

    results = []
    total_tokens = 0
    for i in ranked:
        if scores[i] <= 0:
            continue
        m = meta[i]
        entry = {"rel": m["rel"], "title": m["title"], "score": round(float(scores[i]), 3)}
        if args.layer == 0:
            pass
        elif args.layer == 100:
            first_line = next((l for l in m["body"].split("\n") if l.strip()), "")
            entry["summary"] = first_line[:160]
        elif args.layer == 800:
            entry["excerpt"] = m["body"][:2400]  # ~ 600-800 토큰 근사
        total_tokens += approx_tokens(json.dumps(entry, ensure_ascii=False))
        results.append(entry)
        if total_tokens >= args.layer * 10:
            break  # 안전 상한

    print(json.dumps({
        "query": args.query,
        "layer": args.layer,
        "budget_target_tokens": args.layer,
        "results": results,
        "token_estimate": total_tokens,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
