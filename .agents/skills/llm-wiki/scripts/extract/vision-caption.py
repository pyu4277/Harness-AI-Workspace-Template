#!/usr/bin/env python3
"""
vision-caption.py -- 이미지 캡션 생성 (Claude 내장 vision 위임)
Reference-Port: Graphify semantic pass 중 image 부분 — 우리 시스템은 LLM 호출을 상위 agent 에 위임.

이 스크립트는 metadata (파일 크기, 해상도) 만 추출 + subagent 호출 지시 JSON 반환.
실제 caption 은 호출 측 subagent (semantic-extractor) 가 수행.
"""
import sys
import json
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: vision-caption.py <image>"}))
        sys.exit(1)
    p = Path(sys.argv[1])
    if not p.exists():
        print(json.dumps({"error": "file not found"}))
        sys.exit(1)

    meta = {
        "file": str(p),
        "size_bytes": p.stat().st_size,
        "suffix": p.suffix.lower(),
        "caption": None,  # subagent 가 채움
        "delegation": {
            "target_subagent": "semantic-extractor",
            "task": "image_caption",
            "prompt_hint": f"Describe image at {p} in Korean, max 80 chars.",
        },
    }
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
