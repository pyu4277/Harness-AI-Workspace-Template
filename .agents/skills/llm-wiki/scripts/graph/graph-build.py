#!/usr/bin/env python3
"""
graph-build.py -- WIKI_ROOT 페이지에서 graph.json 생성
Reference-Port: networkx DiGraph 알고리즘만 사용.

출력: WIKI_ROOT/990_Meta/graph.json
  { nodes: [{id, domain, title}], edges: [{src, dst}], stats: {...} }
"""
import os
import re
import sys
import json
from pathlib import Path


def find_wiki_root():
    env = os.environ.get("WIKI_ROOT")
    if env:
        return Path(env).resolve()
    cwd = Path.cwd()
    return (cwd.parent / "001_Wiki_AI").resolve()


MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+\.md)\)")


def main():
    try:
        import networkx as nx
    except ImportError:
        print(json.dumps({"error": "networkx not installed"}))
        sys.exit(1)

    root = find_wiki_root()
    if not root.exists():
        print(json.dumps({"error": f"WIKI_ROOT not found: {root}"}))
        sys.exit(1)

    g = nx.DiGraph()
    for md in root.rglob("*.md"):
        rel = md.relative_to(root).as_posix()
        top = rel.split("/", 1)[0] if "/" in rel else ""
        if top in ("000_Raw", "Clippings", ".obsidian") or "archive" in rel:
            continue
        title = md.stem
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^title:\s*\"?([^\"\n]+)\"?", text, re.M)
            if m:
                title = m.group(1).strip()
        except Exception:
            text = ""
        g.add_node(rel, domain=top, title=title)

        for link_m in MD_LINK.finditer(text):
            target = link_m.group(2)
            if target.startswith("http"):
                continue
            target_abs = (md.parent / target).resolve()
            try:
                target_rel = target_abs.relative_to(root).as_posix()
            except ValueError:
                continue
            g.add_edge(rel, target_rel)

    meta = root / "990_Meta"
    meta.mkdir(exist_ok=True)
    out = meta / "graph.json"

    payload = {
        "nodes": [{"id": n, **g.nodes[n]} for n in g.nodes],
        "edges": [{"src": u, "dst": v} for u, v in g.edges],
        "stats": {
            "node_count": g.number_of_nodes(),
            "edge_count": g.number_of_edges(),
            "generated": "graph-build.py",
        },
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"written": str(out), "nodes": g.number_of_nodes(), "edges": g.number_of_edges()}))


if __name__ == "__main__":
    main()
