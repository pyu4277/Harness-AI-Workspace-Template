#!/usr/bin/env python3
"""
wiki-mcp-server.py -- 자체 MCP 서버 (stdio transport)
Reference-Port: Graphify MCP tools 시그니처 (query_graph / get_node / get_neighbors / search_bm25)
  — 시그니처만 차용, 구현은 자체.

프로토콜: JSON-RPC over stdio (MCP 표준 간소화 스텁).
본 Phase 2 는 MCP SDK 통합 전 최소 스모크 서버 — 실제 MCP Python SDK 는
후속 Phase 에서 교체 가능.
"""
import sys
import json
import os
from pathlib import Path

# Windows cp949 회피
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def wiki_root():
    env = os.environ.get("WIKI_ROOT")
    return Path(env).resolve() if env else (Path.cwd().parent / "001_Wiki_AI").resolve()


def load_graph():
    gp = wiki_root() / "990_Meta" / "graph.json"
    if not gp.exists():
        return {"nodes": [], "edges": []}
    return json.loads(gp.read_text(encoding="utf-8"))


def tool_query_graph(params):
    g = load_graph()
    return {"node_count": len(g["nodes"]), "edge_count": len(g["edges"])}


def tool_get_node(params):
    node_id = params.get("id", "")
    g = load_graph()
    for n in g["nodes"]:
        if n["id"] == node_id:
            return n
    return {"error": "not found", "id": node_id}


def tool_get_neighbors(params):
    node_id = params.get("id", "")
    g = load_graph()
    neighbors = set()
    for e in g["edges"]:
        if e["src"] == node_id:
            neighbors.add(e["dst"])
        elif e["dst"] == node_id:
            neighbors.add(e["src"])
    return {"id": node_id, "neighbors": sorted(neighbors)}


def tool_search_bm25(params):
    query = params.get("query", "")
    if len(query) > 500:
        return {"error": "query too long (max 500 chars)"}
    if not all(c.isprintable() or c.isspace() for c in query):
        return {"error": "query contains non-printable characters"}
    from subprocess import run, PIPE
    script = Path(__file__).resolve().parent.parent / "skills" / "llm-wiki" / "scripts" / "wiki-query.py"
    if not script.exists():
        return {"error": "wiki-query.py missing"}
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    r = run([sys.executable, str(script), query, "--layer", "100"],
            stdout=PIPE, stderr=PIPE, text=True,
            encoding="utf-8", errors="replace", env=env)
    try:
        return json.loads(r.stdout)
    except Exception as e:
        return {"error": str(e), "raw": r.stdout[:300]}


TOOLS = {
    "query_graph": tool_query_graph,
    "get_node": tool_get_node,
    "get_neighbors": tool_get_neighbors,
    "search_bm25": tool_search_bm25,
}


def serve_stdio():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            print(json.dumps({"error": "invalid JSON", "raw": line}), flush=True)
            continue
        tool = req.get("tool", "")
        params = req.get("params", {})
        handler = TOOLS.get(tool)
        if not handler:
            print(json.dumps({"error": f"unknown tool: {tool}",
                              "available": list(TOOLS.keys())}), flush=True)
            continue
        try:
            print(json.dumps({"tool": tool, "result": handler(params)},
                             ensure_ascii=False), flush=True)
        except Exception as e:
            print(json.dumps({"tool": tool, "error": str(e)}), flush=True)


def dispatch_once(tool: str, params: dict):
    """CLI 스모크: 단일 요청 처리."""
    handler = TOOLS.get(tool)
    if not handler:
        print(json.dumps({"error": f"unknown tool: {tool}", "available": list(TOOLS.keys())}))
        return 1
    print(json.dumps({"tool": tool, "result": handler(params)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--once":
        tool = sys.argv[2] if len(sys.argv) > 2 else ""
        params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        sys.exit(dispatch_once(tool, params))
    serve_stdio()
