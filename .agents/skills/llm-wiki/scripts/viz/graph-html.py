#!/usr/bin/env python3
"""
graph-html.py -- graph.json → 정적 HTML 시각화 (오프라인, CDN 無)
Reference-Port: pyvis 의존 없이 D3 없이 순수 HTML/SVG 로 최소 시각화.

입력: WIKI_ROOT/990_Meta/graph.json
출력: WIKI_ROOT/990_Meta/graph.html (정적)
"""
import os
import sys
import json
import math
from pathlib import Path


def find_wiki_root():
    env = os.environ.get("WIKI_ROOT")
    return Path(env).resolve() if env else (Path.cwd().parent / "001_Wiki_AI").resolve()


HTML_TEMPLATE = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<title>Wiki Graph</title>
<style>
  body {{ margin: 0; background: #111; color: #eee; font-family: monospace; }}
  svg {{ width: 100vw; height: 100vh; }}
  .node {{ fill: #4a9; }}
  .node:hover {{ fill: #fd6; }}
  .edge {{ stroke: #555; stroke-width: 0.5; fill: none; }}
  .label {{ fill: #aaa; font-size: 10px; pointer-events: none; }}
  #info {{ position: fixed; top: 8px; left: 8px; background: rgba(0,0,0,.6); padding: 6px 10px; }}
</style></head><body>
<div id="info">nodes: {node_count} · edges: {edge_count} · domains: {domain_count}</div>
<svg viewBox="0 0 {W} {H}">
{edges_svg}
{nodes_svg}
</svg></body></html>
"""


def main():
    root = find_wiki_root()
    gpath = root / "990_Meta" / "graph.json"
    if not gpath.exists():
        print(json.dumps({"error": f"graph.json not found: {gpath}"}))
        sys.exit(1)

    data = json.loads(gpath.read_text(encoding="utf-8"))
    nodes = data["nodes"]
    edges = data["edges"]

    W, H = 1600, 1000
    # 원형 레이아웃 (구현 간결)
    n = max(1, len(nodes))
    positions = {}
    for i, node in enumerate(nodes):
        angle = (i / n) * 2 * math.pi
        r = 400
        x = W / 2 + r * math.cos(angle)
        y = H / 2 + r * math.sin(angle)
        positions[node["id"]] = (x, y)

    edges_svg_lines = []
    for e in edges[:2000]:  # 상한
        p1 = positions.get(e["src"])
        p2 = positions.get(e["dst"])
        if not p1 or not p2:
            continue
        edges_svg_lines.append(
            f'<line class="edge" x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" '
            f'x2="{p2[0]:.1f}" y2="{p2[1]:.1f}"/>')

    nodes_svg_lines = []
    for node in nodes:
        x, y = positions[node["id"]]
        title = node.get("title", node["id"])
        nodes_svg_lines.append(
            f'<g><circle class="node" cx="{x:.1f}" cy="{y:.1f}" r="3">'
            f'<title>{title}</title></circle></g>')

    domains = {n.get("domain", "") for n in nodes}
    html = HTML_TEMPLATE.format(
        W=W, H=H,
        node_count=len(nodes), edge_count=len(edges), domain_count=len(domains),
        nodes_svg="\n".join(nodes_svg_lines),
        edges_svg="\n".join(edges_svg_lines),
    )
    out = root / "990_Meta" / "graph.html"
    out.write_text(html, encoding="utf-8")
    print(json.dumps({"written": str(out), "nodes": len(nodes), "edges": len(edges)}))


if __name__ == "__main__":
    main()
