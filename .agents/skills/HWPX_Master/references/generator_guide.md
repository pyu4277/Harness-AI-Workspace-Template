# HWPX Document Generator (Track A: 새 문서 생성 가이드)

본 문서는 `/HWPX_Master` 스킬 중 기존 첨부파일 없이 '맨바닥에서 새 HWPX 문서(주로 보고서)를 생성할 때' 참조하는 상세 가이드맵입니다.
이 가이드는 이노베이션아카데미 스타일의 공공/정부 양식 보고서를 JSON 설계도(`config.json`) 기반으로 생성합니다.

## 시스템 동작 개요

1. `generate_hwpx.py`는 `templates/report_gov/`에 있는 스타일 템플릿을 참조합니다.
2. JSON 설정 파일을 통해 본문 텍스트, 제목, 표, 부록 구조 등을 동적으로 받아들입니다.
3. XML을 조합하여 최종 결과물인 `.hwpx`로 빌드합니다.

## 사용법 (How to Use)

에이전트(사용자)는 먼저 JSON 형태의 `config.json` 임시 파일을 만들고, 다음 스크립트를 실행합니다.

```bash
python SKILL_DIR/scripts/generate_hwpx.py --output OUTPUT_PATH --config CONFIG_JSON
```

### Config JSON 구조 및 매핑 규칙 (Config JSON Structure)

```json
{
  "title": "보고서 제목",
  "subtitle": "부제목 (optional)",
  "date": "2026.02.14.",
  "department": "담당부서",
  "include_cover": true,
  "sections": [
    {
      "type": "body",
      "title_bar": "본문 제목",
      "content": [
        {"type": "heading", "text": "첫 번째 항목 (□ 모양의 대제목)"},
        {"type": "paragraph", "text": "본문 내용입니다."},
        {"type": "bullet", "text": "하위 항목 (ㅇ 모양)"},
        {"type": "dash", "text": "세부 항목 (- 모양)"},
        {"type": "star", "text": "상세 내용 (* 모양)"},
        {"type": "table", "caption": "표 제목",
         "headers": ["항목", "내용", "비고"],
         "rows": [["데이터1", "설명1", "비고1"], ["데이터2", "설명2", "비고2"]]},
        {"type": "note", "text": "참고 내용"}
      ]
    },
    {
      "type": "appendix",
      "title_bar": "참고1",
      "appendix_title": "부록 제목",
      "content": [...]
    }
  ]
}
```

### Content Types and Style Mapping (폰트/스타일)

| Type | Marker | Font | Size |
|------|--------|------|------|
| `heading` | □ | HY헤드라인M | 15pt |
| `paragraph` | (none) | 휴먼명조 | 15pt |
| `bullet` | ㅇ | 휴먼명조 | 15pt |
| `dash` | - | 휴먼명조 | 15pt |
| `star` | * | 맑은고딕 | 13pt |
| `table` | (table) | 맑은고딕 | 12pt |
| `title_bar` | (bar) | HY헤드라인M | 20pt |
| `appendix_bar` | (bar) | HY헤드라인M | 16pt |

### Section Types

- **`body`**: Standard report body section with title bar and content
- **`appendix`**: Appendix section with numbered tab (참고1, 참고2, etc.)

---

## 실행 전 주의 사항

* 사용자가 새 문서를 만들어달라고 명확히 지시했을 때만 `generate_hwpx.py`를 호출하여 생성합니다. 기존 HWPX를 편집해달라고 했다면 Track B로 이동하세요.
- `generate_hwpx.py`는 `templates/report_gov/` 자원을 반드시 참조해야 하므로 절대 경로 등 환경 변수 유지에 유의하십시오.
