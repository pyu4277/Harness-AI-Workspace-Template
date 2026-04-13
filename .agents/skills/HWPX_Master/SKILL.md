---
name: HWPX_Master
description: "궁극의 통합 HWPX/HWP(아래아한글) 제어 스킬. HWP 바이너리 입력 시 한컴 오피스 COM 엔진으로 무손실 HWPX 자동 변환(Convert-and-Archive) 후 동일한 4-Track 프로세스로 처리. 빈 문서에서 정부/공공기관 양식 보고서를 새로 생성하거나, 기존 HWPX/HWP 문서를 분석하여 원본의 디테일 포맷(표 너비, 폰트 비율 유지)을 그대로 복원/수정(빈칸 채우기 등)할 때 사용합니다. HWPX 내용 추출 시에도 사용하며, hwpx-cli 기반의 초고속 마크다운 변환 및 다중 문서 RAG 인덱싱 기능을 포함합니다. HWPX/HWP 관련 작업 지시가 있을 때마다 최우선으로 구동됩니다."
---

# HWPX Master AI Agent

HWPX/HWP(아래아한글) 파일과 관련된 모든 조작을 관장합니다. 사용자의 요청(의도)에 맞추어 아래 4가지 **[Track]** 중 하나를 선택하여 작업을 수행하십시오. 상황에 따라 `references/` 가이드 문서를 먼저 읽는 것을 권장합니다.

스크립트 경로: `.agents/skills/HWPX_Master/scripts/`

---

## 입력 전처리 (HWP -> HWPX 자동 변환)

**AI 분석 친화적 포맷 정렬**: 최근 트렌드는 AI가 분석할 수 있는 파일 포맷으로 HWPX(XML/OPC)가 HWP(OLE2 바이너리)보다 훨씬 친숙합니다. 따라서 HWP 입력은 자동으로 HWPX로 변환한 후 동일한 Track 처리 흐름을 사용합니다.

### 판별 및 동작

1. **입력 파일 확장자 확인**
   - `.hwpx` -> 바로 Track 진입
   - `.hwp` -> **자동 변환 필수** (아래 절차)
2. **HWP -> HWPX 자동 변환**
   - 실행: `python scripts/convert_hwp_to_hwpx.py <hwp-path>`
   - 엔진: pywin32 COM (`HWPFrame.HwpObject`) + 한컴 오피스 13.0+
   - 방식: `RegisterModule("FilePathCheckDLL", "AutomationModule")` -> `Open(src, "HWP")` -> `SaveAs(dst, "HWPX")`
   - 검증: 출력 .hwpx 의 ZIP 시그니처 (`PK\x03\x04`), mimetype (`application/hwp+zip`), section0.xml 의 문단/표/런/텍스트 노드 카운트 기록
   - **원본 아카이브**: 변환 검증 성공 시 원본 `.hwp` 는 같은 폴더의 `.hwp-archive/YYMMDD-HHMMSS_원본명.hwp` 로 이동 (영구 삭제 금지, 복구 가능)
   - **결과물 위치**: 변환된 `.hwpx` 는 원본 .hwp 가 있던 자리에 생성
3. **변환 후 Track 진입**
   - 변환된 .hwpx 를 입력으로 하여 Track A/B/C/D 중 적절한 Track 선택
   - 이후 처리는 일반 HWPX 와 동일

### 변환 실패 시

- 원본 .hwp 는 그대로 유지 (아카이브 이동 안 함)
- 부분 생성된 .hwpx 는 자동 삭제
- 사용자에게 오류 메시지 (RuntimeError, 파일 경로, 검증 details) 보고
- 한컴 오피스 미설치 / pywin32 미설치 / COM 초기화 실패 등 원인 구분

### 보안/안전 원칙

- **영구 삭제 금지**: 원본 .hwp 는 반드시 `.hwp-archive/` 로 이동 (사용자가 직접 삭제할 책임 유지)
- **변환 검증 필수**: 검증 실패 시 원본 유지 + 생성 파일 삭제 (원자적 동작)
- **절대경로 사용**: `convert_hwp_to_hwpx.py` 는 내부적으로 `os.path.abspath` 로 정규화

### 예시 호출

```bash
# 단일 .hwp 변환
python .agents/skills/HWPX_Master/scripts/convert_hwp_to_hwpx.py "path/to/document.hwp"

# JSON 결과
python .agents/skills/HWPX_Master/scripts/convert_hwp_to_hwpx.py "path/to/document.hwp" --json
```

성공 시 stdout 에 변환된 .hwpx 절대경로 출력. JSON 모드에서는 `{status, hwpx_path, archive_path, stats: {size, paragraphs, tables, runs, text_nodes}}` 반환.

---

## 4-Track 프로세스

### [Track A] 새 문서 자동 생성 모드 (Generator)

- **적용**: 사용자가 "보고서 양식으로 문서 하나 만들어줘", "새로운 공문을 작성해줘" 등 원본 **첨부 없이 새롭게(New)** HWPX를 만들어 달라고 요청할 때.
- **방식**: JSON 설계도를 먼저 작성 후 `scripts/generate_hwpx.py` 또는 `scripts/build_hwpx.py`를 실행하여, 내장된 `report_gov`(정부 보고서) 양식 등에 맞춘 새 문서를 바닥부터 생성합니다.
- **상세 가이드**: `references/generator_guide.md` 참조.

### [Track B] 기존 양식 복원 및 데이터 채우기 모드 (Auto-fill & Restoration)

- **적용**: 사용자가 **기존 `.hwpx` 양식을 업로드**하고 "여기에 표 빈칸 채워줘", "문서 내용 기존 폰트 체계 맞춰서 수정해줘" 라고 할 때.
- **방식**: 기존의 복잡한 레이아웃(표 너비, 여백 등)을 유지하기 위해 `scripts/build_hwpx.py` 등 XML 메타인지 기반의 치환 함수를 작동합니다.
- **상세 가이드**: `references/restoration_guide.md` 참조.

### [Track C] 정보 분리 및 고속 마크다운 추출 모드 (Extraction)

- **적용**: 첨부된 한글 문서에 어떤 내용이나 데이터가 들어 있는지 물어볼 때, 또는 다량의 HWPX 문서를 RAG 검색용으로 변환할 때.
- **방식**: `@masteroflearning/hwpx-cli` 엔진을 호출하여 OCR 없이 순수 텍스트와 표를 마크다운으로 추출합니다.

```bash
npx @masteroflearning/hwpx-cli hwpx-to-md [입력파일.hwpx] -o [출력.md]
```

- 또는 `scripts/text_extract.py` 사용 가능.

### [Track D] 윈도우 OLE 자동화 모드 (Advanced OLE Automation)

- **적용**: XML만으로 제어하기 힘든 세밀한 한글 프로그램 고유 속성 제어가 필요할 때 (이미지 삽입, 복잡한 테두리 서식 등).
- **방식**: `scripts/insert_image_ole.py`를 사용하여 `win32com.client`로 한글 프로그램 OLE 객체를 직접 제어.
- **제약**: Windows 환경에서 한글 프로그램(5.0+)이 설치되어 있어야만 동작.

---

## 의사 결정 흐름 (Decision Tree)

1. **첨부된 파일 포맷 확인**
   - `.hwp` -> **자동 변환 먼저**: `scripts/convert_hwp_to_hwpx.py` 실행 -> 변환된 .hwpx 로 다음 단계 진입
   - `.hwpx` -> 바로 다음 단계 진입
   - 첨부 없음 -> 새 문서가 필요한가? -> **Track A**
2. **작업 의도 분류** (HWPX 기준)
   - 내용을 추출하는가? -> **Track C**
   - 빈칸을 채우거나 특정 단어를 대체하는가? -> **Track B**
   - 이미지 삽입 등 세밀한 서식 제어가 필요한가? -> **Track D**
3. 트랙을 결정했다면, **반드시 관련된 `references/` 가이드 문서를 먼저 읽고** 지시에 따라 진행할 것.

---

## 공통 실행 원칙

- 모든 스크립트는 `scripts/` 디렉토리에 존재합니다. 절대경로 하드코딩 금지, 상대경로 기반으로 탐색.
- 산출물은 프로젝트의 `Output/` 폴더 또는 명확히 지정된 경로에 저장.
- 복잡한 수정 시: `scripts/office/unpack.py`로 압축 해제 → XML 수정 → `scripts/office/pack.py`로 재결합.
- 에러 발생 시 `auto-error-recovery` 스킬 호출.
- **HWP 입력 처리**: 위의 "입력 전처리" 섹션 참조. `.hwp` 는 반드시 `scripts/convert_hwp_to_hwpx.py` 로 변환 후 Track 진입. 원본 .hwp 는 `.hwp-archive/` 로 이동 (영구 삭제 금지).
