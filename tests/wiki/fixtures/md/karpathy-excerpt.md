---
title: "Karpathy LLM Wiki Excerpt"
type: source
domain: 010_Verified
schema_version: 2
created: 2026-04-13
tags: [llm, transformer, attention]
---

# Karpathy LLM Wiki — Excerpt

LLM 위키는 학습한 내용을 영구적으로 보존하는 외부 두뇌 역할을 한다.
핵심 원칙: **0-token retrieval first**, **graph-as-source-of-truth**.

## Attention 메커니즘

Transformer 의 self-attention 은 query-key-value 삼중항으로 표현된다.
[Vaswani, 2017] 에서 처음 제안되었으며 doi:10.48550/arXiv.1706.03762 참조.

## 3-layer 검색

| Layer | 토큰 | 용도 |
|-------|------|------|
| 0 | 0 | 링크 리스트만 |
| 1 | 100 | frontmatter + 1줄 요약 |
| 2 | 800 | 본문 + 인용 |

[[graphify-v1]] 에서 동일 패턴을 확인할 수 있다.
