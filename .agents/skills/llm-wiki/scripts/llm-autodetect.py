#!/usr/bin/env python3
"""
llm-autodetect.py -- 환경에서 사용 가능한 LLM 을 자동 탐지
Reference-Port: MindVault LLM autodetect 아이디어

탐지 우선순위:
  1. Anthropic API Key (ANTHROPIC_API_KEY)
  2. OpenAI API Key (OPENAI_API_KEY)
  3. Ollama localhost:11434
  4. AST-only fallback (LLM 불필요)

출력: stdout JSON { provider, details, fallback? }
"""
import os
import sys
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def detect():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return {"provider": "anthropic", "model_hint": "claude-opus-4-6"}
    if os.environ.get("OPENAI_API_KEY"):
        return {"provider": "openai", "model_hint": "gpt-4o"}
    # Ollama probe
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=1) as resp:
            if resp.status == 200:
                return {"provider": "ollama", "endpoint": "http://localhost:11434"}
    except Exception:
        pass
    return {"provider": "ast-only", "fallback": True,
            "note": "No LLM detected — tree-sitter AST + regex only"}


if __name__ == "__main__":
    print(json.dumps(detect(), ensure_ascii=False))
