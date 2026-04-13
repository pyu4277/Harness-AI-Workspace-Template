#!/usr/bin/env python3
"""
ast-extractor.py -- 소스 코드에서 함수/클래스 AST 노드 추출
Reference-Port 출처: Graphify "tree-sitter AST pass" 아이디어만 차용 (코드 복사 없음)

입력: argv[1] = 파일 경로
출력: stdout JSON { file, language, nodes: [{type, name, start_line, end_line}], skipped? }
규칙: tree-sitter 언어 바인딩 부재 시 graceful skip — harness 흐름 차단 금지.
"""
import sys
import json
import re
from pathlib import Path

LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".go": "go", ".rs": "rust", ".java": "java",
    ".c": "c", ".cpp": "cpp", ".md": "markdown",
}


def regex_fallback(text: str, lang: str):
    """언어별 tree-sitter 바인딩이 없을 때 최소 정규식 추출."""
    nodes = []
    if lang == "python":
        for m in re.finditer(r"^(?:async\s+)?def\s+([A-Za-z_]\w*)", text, re.M):
            nodes.append({"type": "function", "name": m.group(1),
                          "start_line": text[:m.start()].count("\n") + 1})
        for m in re.finditer(r"^class\s+([A-Za-z_]\w*)", text, re.M):
            nodes.append({"type": "class", "name": m.group(1),
                          "start_line": text[:m.start()].count("\n") + 1})
    elif lang in ("javascript", "typescript"):
        for m in re.finditer(r"function\s+([A-Za-z_$][\w$]*)", text):
            nodes.append({"type": "function", "name": m.group(1),
                          "start_line": text[:m.start()].count("\n") + 1})
        for m in re.finditer(r"class\s+([A-Za-z_$][\w$]*)", text):
            nodes.append({"type": "class", "name": m.group(1),
                          "start_line": text[:m.start()].count("\n") + 1})
    elif lang == "markdown":
        for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.M):
            nodes.append({"type": "heading", "name": m.group(2).strip(),
                          "level": len(m.group(1)),
                          "start_line": text[:m.start()].count("\n") + 1})
    return nodes


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: ast-extractor.py <file>"}))
        sys.exit(1)
    p = Path(sys.argv[1])
    if not p.exists():
        print(json.dumps({"error": "file not found", "path": str(p)}))
        sys.exit(1)

    lang = LANG_MAP.get(p.suffix.lower(), "unknown")
    text = p.read_text(encoding="utf-8", errors="replace")

    # tree-sitter 사용 시도 — 바인딩 없으면 regex fallback
    nodes = []
    used_fallback = True
    try:
        import tree_sitter  # noqa: F401
        # 실제 파서 바인딩 로드는 별도 단계 — 본 Phase 2는 존재 확인 + regex fallback
        nodes = regex_fallback(text, lang)
    except ImportError:
        nodes = regex_fallback(text, lang)

    print(json.dumps({
        "file": str(p),
        "language": lang,
        "nodes": nodes,
        "node_count": len(nodes),
        "fallback": used_fallback,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
