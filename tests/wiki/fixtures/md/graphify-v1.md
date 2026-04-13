---
title: "Graphify v1"
type: source
domain: 010_Verified
schema_version: 1
created: 2026-04-13
tags: [graph, mcp]
---

# Graphify v1 — Initial

MCP tools 시그니처:
- `query_graph(cypher: str)` — Cypher-like 쿼리
- `get_node(id: str)`
- `get_neighbors(id: str, depth: int)`

[[karpathy-excerpt]] 의 그래프 표현과 호환된다.
