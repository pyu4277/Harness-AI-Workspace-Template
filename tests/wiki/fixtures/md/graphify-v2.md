---
title: "Graphify v2"
type: source
domain: 010_Verified
schema_version: 2
created: 2026-04-13
tags: [graph, mcp, search]
---

# Graphify v2 — Updated

MCP tools 시그니처 (v2 추가):
- `query_graph(cypher: str)`
- `get_node(id: str)`
- `get_neighbors(id: str, depth: int)`
- `search_bm25(q: str, top_k: int)`  ← v2 신규

스키마 진화: schema_version 1 → 2 마이그레이션.
[[karpathy-excerpt]] 의 attention 항목과 cross-link.
