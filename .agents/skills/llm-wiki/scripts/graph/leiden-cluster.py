#!/usr/bin/env python3
"""
leiden-cluster.py -- Leiden 커뮤니티 탐지 + 우리 스키마 변환
Reference-Port: leidenalg + python-igraph 알고리즘 라이브러리 사용 (통합 제품 X)

입력: stdin JSON { nodes: [id...], edges: [[src, dst, weight?], ...] }
출력: stdout JSON { communities: { id -> community_idx }, n_communities, modularity }
"""
import sys
import json


def main():
    data = json.loads(sys.stdin.read() or "{}")
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not nodes:
        print(json.dumps({"error": "empty graph"}))
        sys.exit(1)

    try:
        import igraph as ig
        import leidenalg
    except ImportError as e:
        print(json.dumps({"error": "igraph/leidenalg not installed", "detail": str(e)}))
        sys.exit(1)

    node_idx = {n: i for i, n in enumerate(nodes)}
    es = []
    weights = []
    for e in edges:
        src, dst = e[0], e[1]
        w = e[2] if len(e) > 2 else 1.0
        if src in node_idx and dst in node_idx:
            es.append((node_idx[src], node_idx[dst]))
            weights.append(float(w))

    g = ig.Graph(n=len(nodes), edges=es, directed=False)
    g.es["weight"] = weights if weights else None

    part = leidenalg.find_partition(
        g, leidenalg.ModularityVertexPartition,
        weights="weight" if weights else None,
        seed=42,
    )

    result = {
        "communities": {nodes[i]: part.membership[i] for i in range(len(nodes))},
        "n_communities": len(set(part.membership)),
        "modularity": round(part.modularity, 4),
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
