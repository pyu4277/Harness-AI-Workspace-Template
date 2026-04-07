# HWPX Auto-fill & Restoration Guide (Track B / C)

본 문서는 `/HWPX_Master` 스킬 중에서 기존 HWPX 문서를 안전하게 복원, 필드 치환 및 텍스트를 추출할 때 사용하는 강력한 가이드맵입니다.
기존 문서에 포함된 특정 양식(폰트 비율, 표 사이즈, 들여쓰기 등)을 99% 유지하며 내용만 정교하게 채워넣거나 추출하는 핵심 로직입니다.

## 1. Track B: 기존 HWPX 원본 양식 기반의 데이터 채우기 (Auto-fill)

기존 문서가 첨부되었고, "표의 빈칸을 채워줘" 라든가 "작성 양식에 맞춰 문서를 만들어줘"와 같은 요청이 있을 경우, 이 Track B를 통해 동작합니다.

### A. 핵심 알고리즘 및 규칙

1. **Unpack & Meta-Analyze 가능성**:
   `scripts/analyze_template.py` 를 활용하여 원본 문서의 구조(텍스트 단락, 표 구조)를 분석할 수 있습니다.
2. **Template Data 치환**:
   `scripts/build_hwpx.py` 스크립트는 원본 `.hwpx`와 JSON 데이터를 결합하여 완성된 `.hwpx` 문서를 반환합니다.
   - 내부적으로 HWPX(.zip)를 풀고 `Contents/section0.xml` 의 `<hp:t>` 태그만 치환합니다.
   - 폰트 스타일, 문단 모양 유지율이 99% 달합니다.
3. **가이드레일 체크 (생략 가능하나 권장)**:
   `scripts/page_guard.py` 를 수행하여 원본 양식의 페이지 수를 넘지 않는지(레이아웃 침범) 검사할 수 있습니다.

### B. 파이썬 빌더 실행법

```bash
python SKILL_DIR/scripts/build_hwpx.py --hwpx "Original.hwpx" --output "Filled.hwpx" --data "data.json"
```

- `data.json`은 채워 넣을 필드 이름(Placeholder) 혹은 타겟 문자와 매칭할 결과값의 Key-Value 형식입니다.

### C. 수동 XML 조작 시 고려사항 (최후 수단)

* HWPX는 XML Zip 구조입니다. 필연적으로 HWPX를 뜯어야 할 경우:
  1. `office/unpack.py --hwpx FILE --dest DIR`
  2. `Contents/section0.xml`을 파싱하여 변경.
  3. `office/pack.py --src DIR --dest NEW_HWPX` 로 강제 결합.
- 수동 조작 시 `<hp:t>` 태그 이외의 레이아웃 태그를 훼손하지 마십시오.

---

## 2. Track C: 문서 텍스트 고속 추출 및 인덱싱 (Extraction via hwpx-cli)

문서를 요약하거나 정보를 묻는 요청, 혹은 여러 문서의 데이터를 RAG용으로 준비할 때 사용합니다. `hwpx-cli` 코어 엔진을 사용하여 표 구조와 텍스트를 고품질 마크다운으로 추출합니다.

### A. 추출 실행법 (단일 문서)

```bash
# 로컬 npx를 통해 hwpx-cli 단일 문서 마크다운 파싱
npx @masteroflearning/hwpx-cli hwpx-to-md "Source.hwpx" "extracted.md"
```

### B. 배치 마크다운 추출 및 인덱싱 (다중 문서)

```bash
# 특정 디렉토리 전체를 파싱하여 RAG용 마크다운으로 청크 분할 및 인덱싱
npx @masteroflearning/hwpx-cli hwpx-to-md "InputDirectory" "OutputDirectory" --chunk 1000 --batch
```

- 단순히 파이썬 스크립트를 쓰던 과거 방식(text_extract.py)보다 월등히 빠르고 안정적인 마크다운 포맷팅 결과를 보장합니다.

---

## 중요 경고

- `build_hwpx.py`는 가능한 원본 서식을 복사/보정하여 새 내용을 주입합니다. 만약 완전히 바닥부터 새로운 양식을 만들어야 한다면 이 문서를 벗어나 **Track A (Generator)** 가이드를 참조하십시오.
- HWPX 압축 및 해제 과정에서 절대경로를 사용하고 중의적인 파일명 충돌을 피하십시오.
