---
title: "E2E Fixtures"
type: reference
domain: tests
schema_version: 2
created: 2026-04-13
---

# E2E Fixtures (Reference-Port 인용)

소형 fixture 셋 — 6개 시나리오용. 외부 패키지 미포함.

## Provenance

| 파일 | 출처 | 라이선스 |
|------|------|---------|
| `md/karpathy-excerpt.md` | Karpathy LLM Wiki Gist 정본 발췌 | 인용 (Reference-Port) |
| `md/graphify-v1.md`, `v2.md` | Graphify README 압축 | 인용 |
| `md/clippings-sample-{1,2,3}.md` | 합성 (3-layer 분배 검증용) | 자체 |
| `pdf/karpathy-llm101.pdf` | 합성 텍스트 PDF (1-2p) | 자체 |
| `audio/short-30s.wav` | 무음 30초 | 자체 |
| `image/chart-flow.png` | 1×1 PNG 합성 | 자체 |
| `office/notes.docx`, `notes.pptx` | zipfile 합성 | 자체 |
| `chaos/*` | 인코딩/frontmatter 손상 합성 | 자체 |
| `expected/*.json` | 시나리오 통과 기준 | 자체 |

## Encoding 강제

- 모든 텍스트: UTF-8, LF, BOM 없음
- 시나리오 진입 시 `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`
- BOM 검출 시 시나리오 abort
