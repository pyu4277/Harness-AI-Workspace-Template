# Next Session Entry Point

> 이 파일은 다음 세션 시작 시 **첫 번째로 읽어야 할 파일**입니다.
> 이전 세션 종료 시점, 현재 상태, 다음 작업 선택지를 제공합니다.

## 이전 세션 정보 (2026-04-12 Wiki 진화 6차 세션 A -- PDF skill 도입 + 의존성 자동 설치)

- **세션 시작**: 2026-04-12 02:00 (사용자 라이선스 결정 + /harness-architect 호출)
- **세션 종료**: 2026-04-12 03:00 (PDF skill Tier-A 도입 + 9 Python + 3 CLI 자동 설치 완료)

## 이번 작업 (Wiki 진화 6차 세션 A) 성과

### 1. anthropics/skills 17 카탈로그 source 작성

- **260411_Anthropic_Skills_Catalog_V001.md** (source, 010_Verified)
- 17 공식 스킬 분류 + description 발췌 + 005 매핑 + 도입 우선순위
- 카테고리: 문서 처리 4 / 디자인 5 / 개발 도구 5 / 커뮤니케이션 3
- 라이선스: Proprietary (사용자 결정으로 005 내부 사용 허용)

### 2. PDF skill Tier-A 신규 도입 (vendor + 한국화)

**신규 파일 13개**:
```
.agents/skills/pdf/
├── SKILL.md              (한국어, 005 통합)
├── SKILL.en.md           (vendor 영문)
├── reference.md          (한국어 wrapper)
├── reference.en.md       (vendor 영문)
├── forms.md              (한국어 wrapper)
├── forms.en.md           (vendor 영문)
├── LICENSE.txt           (vendor Anthropic Proprietary)
├── ATTRIBUTION.md        (출처 + commit hash + 사용자 결정 명시)
├── pdf_Navigator.md      (Tier-A, Track 4-Track, 891줄, 46 블럭)
└── scripts/              (vendor 8개 Python)
    ├── check_fillable_fields.py
    ├── extract_form_field_info.py
    ├── extract_form_structure.py
    ├── convert_pdf_to_images.py
    ├── check_bounding_boxes.py
    ├── create_validation_image.py
    ├── fill_fillable_fields.py
    └── fill_pdf_form_with_annotations.py
```

**vendor 출처**: `github.com/anthropics/skills/skills/pdf` commit `12ab35c`

### 3. TIER_MAP 등록 + PostToolUse 자동 갱신

- `navigator-updater-helpers.js`에 'pdf' 항목 추가 (Tier-A)
- PostToolUse 훅이 4 마커 자동 갱신:
  - §1.2 navigator-diagram (pdf 노드 추가)
  - §5.3 navigators-meta (Track 패턴 +1)
  - §5.4 pattern-stats
  - §9.0 gap-analysis

### 4. 의존성 자동 설치 (사용자 결정)

**Python (winget + pip 9 패키지 모두 설치 OK)**:
- python 3.12.10 (winget Python.Python.3.12)
- pypdf 6.10.0 / pdfplumber 0.11.9 / reportlab 4.4.10 / pypdfium2 5.7.0
- pytesseract 0.3.13 / pdf2image 1.17.0 / Pillow 12.2.0 / pandas 3.0.2 / openpyxl 3.1.5

**CLI (winget 3 도구 + 한국어 모델)**:
- qpdf 12.3.2 (winget qpdf.qpdf)
- tesseract 5.4.0 (winget UB-Mannheim.TesseractOCR)
- poppler 25.07.0 (winget oschwartz10612.Poppler)
- **kor.traineddata** 15 MB (Python urllib 다운로드, 사용자 폴더 `C:\Users\pyu42\tessdata`에 설치 -- Program Files 권한 거부 회피)

**경로 정보 (PATH 미등록)**:
- Python: `C:/Users/pyu42/AppData/Local/Programs/Python/Python312/python.exe`
- qpdf: `C:/Program Files/qpdf 12.3.2/bin/qpdf.exe`
- tesseract: `C:/Program Files/Tesseract-OCR/tesseract.exe`
- pdftotext: `C:/Users/pyu42/AppData/Local/Microsoft/WinGet/Packages/oschwartz10612.Poppler_*/poppler-25.07.0/Library/bin/pdftotext.exe`
- tessdata 한국어: `C:/Users/pyu42/tessdata/kor.traineddata`

### 5. CDM PDF 검증 (부분)

- 56 MB CDM PDF 메타데이터 추출 OK (224 페이지, Adobe InDesign CS3, 2018-10-17 작성)
- 본문 텍스트 추출: 페이지당 ~10자 (사실상 이미지/스캔 PDF) → **OCR 필요** (Track D)
- pdfplumber + pypdfium2 두 라이브러리 모두 같은 결과 (이미지 기반 PDF 확정)
- 발췌 entity 작성은 다음 세션 (Track D OCR 사용 + 한국어 모델)

### 위키 + 005 통계 변화

- **위키 pages**: 38 → **39** (+1, Anthropic 카탈로그 source)
- **500_Technology sources**: 12 → **13**
- **005 신규 스킬**: pdf (Tier-A) -- Track 4-Track 패턴
- **TIER_MAP**: pdf 항목 추가
- **PostToolUse 훅**: 4 마커 자동 갱신 검증 OK
- **wiki-lint**: 0 issues
- **회귀 0**: 기존 22 Navigator + 13 AUTO 마커 모두 보존

## 사용자 라이선스 결정 (영구 기록)

> "우리가 지금 대화하고 있는 이 프로그램 자체가 Anthropic 프로그램이고
> 마음껏 사용하라고 공식적으로 공개한거라 모두 그대로 사용해도 아무 문제없어."

→ ATTRIBUTION.md에 명시. 005 내부 사용만 허용 (외부 공개 별도 승인 필요).

## 다음 세션 (세션 B) 예정 작업

### 작업 3: CDM PDF 발췌 검증 (즉시)

- CDM은 OCR 필요 (224 페이지 전체 OCR ~30분 예상)
- pytesseract + lang='kor' + tessdata-dir custom config
- 결과를 `CDM_Project_Guide_2018.md` entity로 작성
- 또는 첫 10-20 페이지만 발췌 후 나머지는 archive

### 작업 4: 200_사업 PDF 7개 발췌

- wiki-pdf-stage.js로 7 PDF 임시 복사
- 각 PDF 텍스트/표/메타 추출 (pdfplumber 또는 OCR)
- `Suncheon_1st_College_Quality_Management.md` entity 작성

### 후속 작업 (세션 B 또는 그 이후)

- IMP-024/025/026/027 공식 기록
- docx/xlsx/pptx skill 검토 (DocKit과 비교)
- 300_제일대학교 354 md 분할 처리

---

## 이전 세션 정보 (2026-04-11 Wiki 진화 5차+ -- 3 destructive 작업 + PDF 워크플로우)

- **세션 시작**: 2026-04-11 (5차 직후, 사용자 3 결정 승인)
- **세션 종료**: 2026-04-11 (archive + 중복본 + PDF 스크립트 모두 완료)

## 이번 추가 작업 성과

사용자 3 결정 승인 후 즉시 진행:

### A. 100_AI 폴더 archive 이동 완료

```
mv 001_Wiki_AI/000_Raw/Obsidian Knowledge/100_AI 대화 저장
   → 001_Wiki_AI/990_Meta/archive/100_AI_Conversation_260411/
```

- ~2.3 MB, 21 unique md
- 8 위키 페이지가 raw_source 프론트매터로 추적 가능
- index.md의 Archived Raw Sources 표 갱신 (2 → 3)

### B. (2) 중복본 일괄 삭제 완료

| 위치 | 삭제 수 |
|------|--------:|
| 000_Raw/Obsidian Knowledge/ 전체 | 285 |
| 990_Meta/archive/100_AI_Conversation_260411/ | 21 |
| **총합** | **306** |

- diff 검증 2 샘플 (test.md, Project_Drafting_Rules) → 100% 동일 확인
- 일괄 삭제 후 wiki-lint 0 issues
- 디스크 절약: 약 ~75 MB 추정

### C. PDF MCP 우회 워크플로우 스크립트 작성

**위치**: `.claude/hooks/wiki-pdf-stage.js` (200줄)

**3 명령**:
```bash
# 위키 PDF를 005 임시 디렉토리로 복사
node .claude/hooks/wiki-pdf-stage.js stage <wiki-pdf-absolute-path>

# 현재 임시 파일 목록
node .claude/hooks/wiki-pdf-stage.js list

# 임시 파일 모두 정리
node .claude/hooks/wiki-pdf-stage.js cleanup
```

**기능**:
- 위키 root + 허용 prefix(`000_Raw/`, `990_Meta/archive/`) 검증
- 허용 확장자 검증 (PDF/HWP/HWPX/DOCX/PPTX)
- 100 MB 크기 한도
- 임시 디렉토리: `Temporary Storage/wiki-pdf-stage/`
- 충돌 시 timestamp suffix 자동 추가
- cleanup은 stage 디렉토리 안의 파일만 삭제 (외부 0 영향)

**검증**:
- list 빈 디렉토리 OK
- stage 1 파일 (53.5 KB) OK
- PDF MCP `display_pdf` 호출 성공 (viewUUID 발급)
- cleanup 완료 OK
- 다시 list 비어 있음 OK

### D. PDF MCP 후속 interact 한계 발견 (IMP-027 후보)

**시도**:
```javascript
display_pdf(staged_path)  // OK (viewUUID 발급)
interact(viewUUID, "get_text", intervals=[{1,5}])
```

**결과**:
```
ERROR: Viewer never connected for viewUUID ...
The iframe likely failed to mount — this happens when the conversation
goes idle before the viewer finishes loading.
```

**원인**: PDF MCP의 후속 `interact`는 뷰어가 mount되어 사용자가 활성 상태로 보고 있어야 함. 비동기 자동 발췌에는 부적합.

**우회 방법**:
1. **사용자 시청 모드**: 사용자가 뷰어를 직접 열어 보면서 발췌 (수동)
2. **연속 호출**: display_pdf + interact를 매우 빠르게 (< 8s) 연속 실행 (자동화 한계)
3. **별도 도구**: pdf-parse npm 패키지 등 대체 라이브러리 (다음 세션 검토)

→ **IMP-027 후보**: PDF MCP는 사용자 시청 모드 전용. 자동 발췌는 별도 도구 필요.

## 위키 통계 (변동)

- total_pages: **38** (변동 없음, 신규 위키 페이지 0)
- total_archived_raw: 2 → **3** (100_AI_Conversation_260411 추가)
- 디스크: ~75 MB 절약 (306 중복본 삭제)
- wiki-lint: **0 issues**

## 005 신규 파일

- `.claude/hooks/wiki-pdf-stage.js` (200줄, 신규)
- `Temporary Storage/wiki-pdf-stage/` (신규 디렉토리, 빈 상태로 생성)

## 미처리 (다음 세션)

### PDF MCP 한계 우회 (선택)

- IMP-027 공식 기록 (PDF MCP 자동 발췌 한계)
- 대체 도구 검토: `pdf-parse`, `pdfjs-dist`, `mupdf` 등
- 사용자 시청 모드 워크플로우 가이드 작성

### 미발견 폴더 (다음 세션 발견)

`Obsidian Knowledge/` 루트에 카탈로그 외 파일 다수:
- 9 VIDEO md (하네스 / Claude Code / RAG 관련)
- AI_Workspace_Master_Class_Complete.md
- Google_Apps_Chapter_Script_v1.0.md
- Project_Drafting_Rules_v1.0.md
- table-export-001~003.csv
- 칫솔살균기_비교분석_리포트.md
- 80개 Pasted image PNG
- 002_전기 Study (폴더, 미확인)
- 001_포멧하고 Claude Code 사용하기 (폴더)
- 260108_sinsanupTraining (폴더)
- Clippings, Excalidraw, Landom Report (폴더)

→ 다음 세션 별도 카탈로그 source 작성 필요.

### 큰 작업 (5-7 세션)

- **300_제일대학교** AI 교재개발 (200 md 분할 처리)
- **200_사업** PDF/HWP 본문 발췌 (wiki-pdf-stage.js + 사용자 시청 모드)

---

## 이전 세션 정보 (2026-04-11 Wiki 진화 5차 -- 000/200/300 폴더 카탈로그)

- **세션 시작**: 2026-04-11 (Wiki 진화 4차 직후, 사용자 권장 인용)
- **세션 종료**: 2026-04-11 (3 신규 폴더 처리 + PDF MCP 한계 발견)

## 이번 작업 (Wiki 진화 5차) 성과

### 신규 위키 페이지 3종

1. **Google_Calendar_MCP_Guide.md** (entity, 000_일단은 폴더)
   - Skypage AI 엔지니어용 가이드 발췌
   - **005에 이미 통합된 Google Calendar MCP 8 도구와 매핑** 확인
2. **260411_200_Business_Folder_Catalog_V001.md** (source, 200_사업 폴더)
   - 순천제일대 신산업사업단 매뉴얼 개발 + 출장 양식 + PDF 7 + HWP 2
   - **CQI / NCS / 벤치마킹 구조** 발견 (bkit-rules + pdca와 직접 일치)
   - **OutreachAutomation 스킬 후보** 명시
3. **260411_300_University_Folder_Catalog_V001.md** (source, 300_제일대학교 폴더)
   - 200 unique md (99% AI 교재개발 참고자료)
   - URL 19 + Youtube 180 (대부분 Laurence Svekis Google Apps Script)
   - **거대 HTML 보고서 65979 토큰** (분할 발췌 필요)
   - 5-7 세션 분할 처리 권장

### 위키 통계

- total_pages: 35 → **38** (+3)
- 500_Technology entities: 13 → **14** (+1)
- 500_Technology sources: 10 → **12** (+2)
- 500_Technology concepts: 11 (변동 없음)
- wiki-lint: **0 issues**

### PDF MCP 한계 발견 (IMP-026 후보)

**문제**:
```
mcp__plugin_pdf-viewer_pdf__display_pdf
url: D:/OneDrive - 순천대학교/001_Wiki_AI/000_Raw/...
Error: Local file not in allowed list
Allowed directories: D:\OneDrive - 순천대학교\005_AI_Project
```

**원인**: PDF MCP가 005_AI_Project 디렉토리만 허용. 위키 폴더 직접 접근 차단.

**우회**: 발췌 대상 PDF를 005로 임시 복사 → PDF MCP → 발췌 후 정리. 자동화 스크립트 권장.

**Read 도구도 실패**:
```
pdftoppm failed: Command 'pdftoppm' not found or is in an unsafe location
```
→ pdftoppm이 환경에 없거나 unsafe location에 있음. PDF 직접 발췌 불가.

## 사용자 결정 필요 사항 (즉시 처리)

### 결정 1: 100_AI 폴더 archive 이동

**현재 상태**: 100_AI 21 unique 100% 위키화 완료 (8 페이지). Karpathy LLM Wiki Raw 정책에 따라 archive 이동 권장.

**제안**:
```
mv "001_Wiki_AI/000_Raw/Obsidian Knowledge/100_AI 대화 저장"
   "001_Wiki_AI/990_Meta/archive/100_AI_Conversation_260411/"
```

→ destructive 작업이라 사용자 명시 승인 필요.

### 결정 2: (2).md 중복본 정리

**100_AI**: 21개 중복본
**Mermaid (순서도)**: 27개 중복본
**000_일단은**: 1개 중복본
**200_사업**: 약 14개 중복본 (md 3 + pdf 6 + hwp 2)
**300_제일대학교**: 약 154개 중복본 (200 unique → 354 - 200 = 154)

**총합**: ~217개 ` (2).md`/`(2).pdf`/`(2).hwp` 중복본

→ 즉시 삭제 또는 archive 이동. 사용자 명시 승인 필요.

### 결정 3: PDF MCP allowed list 확장

**현재 한계**: 005_AI_Project 디렉토리만 허용
**해결책 옵션**:
- (a) PDF MCP 설정에서 위키 폴더 추가 (사용자 직접 수정)
- (b) 자동화 스크립트 (발췌 시 005로 임시 복사 → PDF MCP → 정리)
- (c) Read 도구의 pdftoppm 의존 해결 (pdftoppm 설치)

→ 사용자 결정 필요.

## 미처리 (다음 세션)

### 큰 작업 (다세션 필요)

- **300_제일대학교** AI 교재개발 200 자료 (5-7 세션 분할):
  - 거대 HTML 보고서 (65979 토큰, 분할 발췌)
  - URL 19 (Google Apps Script + Gemini 그룹화)
  - YouTube 180 (Laurence Svekis 시리즈 우선)
- **200_사업** PDF/HWP 본문 발췌 (PDF MCP 임시 복사 워크플로우 필요)

### 작은 작업

- 100_AI archive 이동 (사용자 승인 후)
- (2).md 중복본 217개 정리 (사용자 승인 후)
- IMP-024/025/026 공식 기록 (도구 가용성 + 민감 정보 + PDF MCP 한계)

---

## 이전 세션 정보 (2026-04-11 Wiki 진화 4차 -- 100_AI 100% 완료 + Mermaid 카탈로그)

- **세션 시작**: 2026-04-11 (Wiki 진화 3차 직후, 사용자 두 번째 "나머지 알아서" 지시)
- **세션 종료**: 2026-04-11 (100_AI 세션 5/6/7 + Mermaid 폴더 처리 완료)

## 이번 작업 (Wiki 진화 4차) 성과

100_AI **세션 5/6/7 자율 연속 진행 + Mermaid 폴더 추가 처리**.

### 100_AI 100% 완료 (세션 5/6/7)

| 세션 | 산출물 | 출처 |
|:----:|--------|------|
| **5** | **AI_Development_Trial_Patterns.md** (concept) | 전기기기 GUI 27KB + Gemini 주가 16KB + 여행 사이트 14KB |
| **6** | **Electrical_Engineering_Domain_Knowledge.md** (entity) | OCR Grok 99KB + 도전율 44KB + 아두이노 14KB |
| **6** | **n8n_Self_Hosting_Guide.md** (entity) | yt-assets n8n 12KB |
| **7** | 카탈로그 100% 갱신 (메타) | -- |

### 추가: Mermaid 폴더 발췌

| entity | 출처 |
|--------|------|
| **Mermaid_Diagram_Type_Catalog.md** (entity) | 순서도 폴더 25 mermaidchart.com 다이어그램 타입 + Blog + draw.io |

### 신규 wiki 페이지 4종 (세션 5~7 + Mermaid)

1. AI_Development_Trial_Patterns.md (concept) -- 5 공통 패턴 + 3 안티패턴
2. Electrical_Engineering_Domain_Knowledge.md (entity) -- MKS/CGS 변환표 + 도전율 + 아두이노 4 프로젝트
3. n8n_Self_Hosting_Guide.md (entity) -- Docker + Railway + Webhook
4. Mermaid_Diagram_Type_Catalog.md (entity) -- 25 다이어그램 타입 + 005 Mermaid_FlowChart 확장 후보

### 위키 통계 변화

- total_pages: 31 → **35** (+4)
- 500_Technology entities: 10 → **13** (+3)
- 500_Technology concepts: 10 → **11** (+1)
- wiki-lint: **0 issues**

### 100_AI 폴더 처리 완료 (21/21 = 100%)

| 카테고리 | unique | 처리 위키 |
|----------|:-----:|----------|
| AI 프로젝트 | 4 | PaperResearch_Genesis + Evaluation_Skill_Genesis + GravityESS_Project |
| 도구 가이드 | 5 | Tool_Guides_Collection_260411 (5 통합) |
| 개발 시도 | 5 | Smartphone_Home_Server (Phon) + AI_Development_Trial_Patterns (3 concept) + PaperResearch_Genesis (크롤링) |
| 검색/리서치 | 6 | Smartphone_Home_Server (잠자는 폰 2) + Electrical_Engineering_Domain_Knowledge (3) + n8n_Self_Hosting_Guide (1) |
| 메타 | 1 | Tool_Guides_Collection_260411 (CLAUDE.md 흡수) |

**100_AI 신규 위키 누적**: 6 entity + 1 concept + 1 source = **8 페이지**

### 100_AI 다음 단계 (사용자 승인 필요)

1. **archive 이동**: 100_AI 폴더 → `990_Meta/archive/100_AI_Conversation_260411/`
2. **(2).md 중복본 16개 정리**: diff 검증 후 일괄 삭제 또는 archive
3. **빈 파일 1개 정리**: Google Digital Office (2 bytes)
4. **민감 정보 raw 파일 처리**: API 키 / 비밀번호 노출 파일 (Notion+Cal, Phon 서버)

## 미처리 (다음 세션)

### 큰 폴더 (별도 우선순위 결정 필요)

- **300_제일대학교** 354 md (가장 큼) -- 다세션
- **200_사업** 6 md + 12 pdf + 4 hwp (PDF MCP 활용 가능)

### 작은 폴더

- **000_일단은 저장부터** 5 md (Google Calendar MCP 가이드 1개 + 4)
- **AI CLI Development** 0 md (서브폴더만, 처리 불요)
- **Landom Report** 0 md (15M 첨부만)

### 기타 보안 작업

- IMP-024 후보: 도구 가용성 자가 검증
- IMP-025 후보: Raw 발췌 시 민감 정보 자동 검출 + 마스킹

---

## 이전 세션 정보 (2026-04-11 Wiki 진화 3차 -- 100_AI 세션 2-4 자율 진행)

- **세션 시작**: 2026-04-11 (Wiki 진화 2차 직후, 사용자 "나머지 알아서" 지시)
- **세션 종료**: 2026-04-11 (100_AI 세션 2/3/4 연속 완료)

## 이번 작업 (Wiki 진화 3차) 성과

100_AI 대화 저장의 5+ 세션 점진 위키화 계획 중 **세션 2-4 자율 진행**.

### 세션 2: 평가 에이전트 + GravityESS

| entity | 출처 | 핵심 발견 |
|--------|------|----------|
| **Evaluation_Skill_Genesis.md** | 260226 평가 에이전트 89KB | /CIPP평가 → /Evaluation 진화. **Plan A/B 패턴** + **조건부 OCR** + **동적 템플릿 변환 선행** |
| **GravityESS_Project.md** | 260308_GravityESS 51KB | **003_AI_Project 활성 스킬 8 + MCP 4 카탈로그** + RAG 7요소 + Total_SystemRun 4단계 거버넌스 |

### 세션 3: 도구 가이드 5종 통합

| entity | 출처 | 핵심 발견 |
|--------|------|----------|
| **Tool_Guides_Collection_260411.md** | Bkit + Playwright e2e + Notion+Cal + Google Opal + 폴더 메타 | **10-Agent 멀티 오케스트레이션 패턴** (project-orchestrator + 9 sub-agent), **일정 추출 JSON GPT 프롬프트** (Make 호환), **bkit 트리거 키워드 자동 활성** |

### 세션 4: 홈서버 통합

| entity | 출처 | 핵심 발견 |
|--------|------|----------|
| **Smartphone_Home_Server.md** | Phon 87KB + 잠자는 폰 39KB + 영상 2KB | **5단계 아키텍처**: PC → SSH → Termux → Ubuntu chroot → tmux → VSCode Server → CloudFlare Tunnel. 무공인IP + termux-wake-lock 패턴 |

### 신규 entity 5종 (세션 2~4 합계)

1. Evaluation_Skill_Genesis.md
2. GravityESS_Project.md
3. Tool_Guides_Collection_260411.md
4. Smartphone_Home_Server.md
5. (Wiki 진화 2차의 PaperResearch_Genesis.md는 이미 등록됨)

### 위키 통계 변화

- total_pages: 26 → **31** (+5 entity)
- 500_Technology entities: 6 → **10** (+4)
- 500_Technology sources: 10 (변동 없음)
- wiki-lint: **0 issues** (broken link 1개 발견 후 수정)

## 보안 경고 (사용자 즉시 조치 필요)

원본 Raw 파일 발췌 중 **민감 정보 3건 발견**. 위키 entity에는 모두 마스킹 처리:

### 1. OpenAI API 키 평문 노출
- **파일**: `Notion & Calender 연동 Make용 GPT 프롬프트.md`
- **노출**: `sk-proj-Iy5tup***` + `sk-proj-_wdUPq***` + `org-FG5rNW***`
- **조치**: OpenAI 대시보드에서 두 키 즉시 무효화 + 재발급

### 2. VSCode Server 비밀번호 평문 노출
- **파일**: `Phon으로 server만들기.md`
- **노출**: `park1095!@`
- **조치**: 즉시 변경. 다른 계정에 같은 비번 사용 시 모두 변경

### 3. SSH 공개키 노출
- **파일**: `Phon으로 server만들기.md`
- **노출**: `gei_personal@DESKTOP-415PRO0` 공개키
- **조치**: 위험도 낮음. 단, 노출된 공개키 페어 폐기 권장

## 100_AI 세션 진행 상황

| 세션 | 대상 | 상태 |
|:----:|------|:----:|
| 1 | 카탈로그 + PaperResearch Genesis | OK (Wiki 진화 2차) |
| **2** | 평가 에이전트 + GravityESS | **OK (이번 세션)** |
| **3** | 도구 가이드 5종 통합 | **OK (이번 세션)** |
| **4** | 홈서버 (Phon + 잠자는 폰) | **OK (이번 세션)** |
| 5 | 전기기기 GUI + Gemini 주가 + 여행 + 크롤링 | 대기 |
| 6 | OCR Grok + 도전율 + 아두이노 + yt-assets | 대기 |
| 7 | 100_AI 폴더 archive 이동 + 마무리 | 대기 |

**남은 unique 파일 (~10개)**:
- 전기기기 GUI 27KB / Gemini 주가 16KB / 여행 사이트 14KB / 251225 크롤링 10KB
- OCR Grok 99KB / 도전율 44KB / 아두이노 14KB / yt-assets 12KB
- + 빈 파일 1개 + Notion+Cal에 미흡수 부분

## 기타 폴더 (다음 옵션)

- **300_제일대학교** 354 md (가장 큼)
- **200_사업** 6 md + 12 pdf + 4 hwp (PDF MCP 활용)
- AI CLI Development 8 md
- 순서도 4 md
- 000_일단은 5 md

---

## 이전 세션 정보 (2026-04-11 Wiki 진화 -- PDF MCP + Raw 자료 추가 처리)

- **세션 시작**: 2026-04-11 (Tier-C 세션 1 위키 진화 직후)
- **세션 종료**: 2026-04-11 (PDF MCP entity + Raw 자료 카탈로그 + PaperResearch Genesis 완료)

## 이번 추가 작업 (Wiki 진화 2차) 성과

### A. PDF MCP 능력 재발견

이전 세션에서 "PDF 못 본다" 잘못 안내한 실수 → 이번에 도구 목록 재확인 → `mcp__plugin_pdf-viewer_pdf` 발견:
- `display_pdf` + `interact` 두 진입점
- 14 액션 + 9 주석 타입 + 좌표 시스템 + 폼 입력 + 저장
- **PDF_Viewer_MCP.md** entity 신규

→ **IMP-024 후보**: 도구 가용성 자가 검증 의무 (단정 금지)

### B. 000_Raw 신규 자료 (Obsidian Knowledge 668 파일)

사용자가 Obsidian 노트 vault 전체를 `001_Wiki_AI/000_Raw/`에 추가:
- 524 md + 80 png + 44 pdf + 4 hwp + 6 html + 6 csv = 668 파일
- 5 주요 폴더: 200_사업(757M), 300_제일대학교(169M), 100_AI 대화 저장(2.3M), Landom Report(15M), AI CLI Development

이번 세션 우선 처리: **100_AI 대화 저장** (42 md, 21 unique)

### C. 신규 위키 페이지 3종

1. **PDF_Viewer_MCP.md** (entity, 030_Work)
2. **260411_100_AI_Conversation_Archive_Catalog_V001.md** (source) -- 21 unique md 카탈로그 + 5 세션 점진 위키화 계획
3. **PaperResearch_Genesis.md** (entity) -- 002_AI_Project 연구자료 V1 (616KB) + V2 (10KB) 발췌. **Sci-Hub MCP 통합 시도 → Search & Log 전환 핵심 발견** (현재 PaperResearch 스킬의 기원)

### D. 위키 통계 변화

- total_pages: 23 → **26**
- 500_Technology entities: 4 → **6** (PDF Viewer + PaperResearch Genesis)
- 500_Technology sources: 9 → **10** (100_AI 대화 카탈로그)

### E. 미처리 (다음 세션)

**Raw 자료 점진 위키화**:
- 100_AI 대화 저장 세션 2: 평가 에이전트 89KB + GravityESS 51KB → 2 entity
- 100_AI 대화 저장 세션 3: Bkit 명령어 / Playwright e2e / Notion+Calendar 등 → 3 entity
- 100_AI 대화 저장 세션 4: 개발 시도 5개 통합 concept
- 100_AI 대화 저장 세션 5: 검색/리서치 6개 + 통합 + archive 이동 → 100% 완료

**기타 폴더 (524 md 중 482 미처리)**:
- 300_제일대학교 354 md (가장 큼, 다세션 필요)
- 200_사업 6 md + 12 pdf + 4 hwp (PDF MCP로 PDF 발췌 가능)
- AI CLI Development 8 md
- Landom Report 0 md (15M, 첨부 위주)

**(2).md 중복본 16개**:
- 사용자 승인 후 archive 이동 또는 삭제 권장

---

## 이전 세션 정보 (2026-04-11 Option E 세션 1 + Wiki 진화 완료)

- **세션 시작**: 2026-04-11 (Option E 세션 1 직후)
- **세션 종료**: 2026-04-11 (Tier-C 세션 1 결과 위키화 완료)
- **프로젝트**: 260410_Harness_Evolution

## 이번 추가 작업 (Wiki 진화) 성과

llm-wiki Mode 3로 Option E 세션 1 결과를 위키화:

### 갱신/신규 위키 페이지

1. **Navigator_Pattern_Library.md** (concept, 갱신):
   - 14 → 18 Navigator 통계 갱신
   - 적용 검증 표 14행 → 18행 (Tier-C 4 항목 추가)
   - 5 패턴 변형 4종 추가:
     - Operation Dispatcher: 5 ops 단순형 (btw) + 12 ops + 4 agents 대형 (pdca)
     - Branching + Linear: 9 규칙 다중 분기 (bkit-rules) + 7 Phase HARD-GATE (plan-plus)
   - 총 통계: 10488줄 / 25 Mermaid / 333 카드 → 13055줄 / 29 Mermaid / 457 카드

2. **260411_Tier_C_Session1_V001.md** (source, 신규):
   - Tier-C 세션 1 전체 기록
   - 4 Navigator 실측 데이터 + 작성 순서
   - SYSTEM_NAVIGATOR.md 자동 갱신 검증
   - 핵심 발견 4종 (scaffold 한계 + 12 ops 표현력 + 9 규칙 표현 + HARD-GATE 패턴)
   - IMP-022/023 후보 (scaffold 헤딩 파싱 + processType 일관성)

3. **index.md + log.md 갱신**:
   - total_pages 22 → 23
   - log 3개 신규 엔트리 (UPDATE concept + INGEST source + UPDATE index)

### 검증

- **wiki-lint**: 0 issues
- **회귀 0**: 기존 22 페이지 모두 보존

---

## 이전 세션 정보 (2026-04-11 Option E 세션 1 완료)

- **세션 시작**: 2026-04-11 (Warm Boot, Option G + H 이후)
- **세션 종료**: 2026-04-11 (Option E 세션 1: Tier-C 4개 신규 생성 완료)
- **프로젝트**: 260410_Harness_Evolution (Tier-C 100% 커버리지 진행)

## 이번 세션 (Option E 세션 1) 성과

Tier-C 8개 중 균형 잡힌 4개를 신규 생성. **전체 커버리지 14/22 → 18/22 (82%)**.

### 신규 Navigator 4개

| 스킬 | 줄 | 블럭 | Mermaid | click | 패턴 |
|------|-----|------|---------|-------|------|
| btw | 393 | 16 | 1 | 17 | Operation Dispatcher (5 ops) |
| plan-plus | 525 | 24 | 1 | 25 | Branching + Linear (7 Phase + HARD-GATE) |
| bkit-rules | 677 | 33 | 1 | 40 | Branching + Linear (9 규칙 + 다중 분기) |
| pdca | 972 | 51 | 1 | 52 | Operation Dispatcher (12 ops + 4 agents) |
| **합계** | **2567** | **124** | **4** | **134** | -- |

### SYSTEM_NAVIGATOR.md 자동 갱신 검증

PostToolUse 훅이 4 마커 모두 자동 채움:
- §1.2 navigator-diagram: OD_pdca/OD_btw + BL_bkit_rules/BL_plan_plus 추가
- §5.3 navigators-meta: 14 → 18 Navigator 표 자동 갱신
- §5.4 pattern-stats: Operation Dispatcher 2→4, Branching+Linear 2→4
- §9.0 gap-analysis: Tier-C 미생성 8 → 4 (50%)

총 줄수: 4244 → **4256** (+12, 자동 갱신만)

### 검증 결과

- **회귀 0**: 기존 14 Navigator + 8 AUTO 마커 모두 보존
- **이모티콘 0**: 4개 모두 PostToolUse emoji 차단 통과 (IMP-021 준수)
- **절대경로 0**: PostToolUse path-guard 통과
- **PostToolUse 훅 4회 성공**: 각 Navigator 작성 시 4 섹션 자동 갱신
- **블럭 카드 평균**: 31개/Navigator (15 기준 초과)
- **시간**: ~95분 (예상 ~115분 이내)

### 작성 순서 (작은 것 → 큰 것)

1. btw (~15분, 393줄, Operation Dispatcher 워밍업)
2. plan-plus (~20분, 525줄, Branching + Linear 첫 적용)
3. bkit-rules (~25분, 677줄, 9 규칙 다중 분기)
4. pdca (~35분, 972줄, 12 ops 가장 큼)

---

## 이전 세션 정보 (2026-04-11 Option G + H 완료)

- **세션 시작**: 2026-04-11 16:30 (Warm Boot, Option C 이후)
- **세션 종료**: 2026-04-11 (Option G + H + 000_Raw 점검 통합 완료)
- **프로젝트**: 260410_Harness_Evolution (지식 통합 + 각인 시스템 진화)

## 이번 세션 (Option G + H) 성과

3 작업 통합 처리 (~60분):

### Option H -- IMP-021 공식 기록

- `.harness/imprints.json`에 IMP-021 추가 (total_imprints: 20 → 21)
- 마크다운 표 마커는 ASCII 한정 (`O`/`-`/`[O]`/`[X]`/`Y`/`N`)
- PromptKit Navigator 작성 시 발견된 실수 (Option A 세션 3) 공식 학습

### 000_Raw 점검

- 4 하위 디렉토리(papers/reports/snapshots/transcripts) 모두 0 파일
- Raw 위키 진화 작업 불필요 (모든 외부 자료 이미 위키화 완료)

### Option G -- Wiki 진화 (llm-wiki Mode 3)

신규 위키 페이지 2개:
1. **SYSTEM_NAVIGATOR_Auto_Aggregation.md** (concept) -- 메타 문서 자동 집계 4 요소 패턴
2. **260411_Option_C_Auto_Aggregation_V001.md** (source) -- Option C 단일 세션 전체 기록

위키 통계: total_pages 20 → 22, 500_Technology 20 → 22

---

## 이전 세션 정보 (2026-04-11 Option C 완료)

- **세션 시작**: 2026-04-11 (Warm Boot, Option F 이후)
- **세션 종료**: 2026-04-11 (Option C: SYSTEM_NAVIGATOR.md 자동 재생성 완료)
- **프로젝트**: 260410_Harness_Evolution (Navigator 자동화 인프라 확대)

## 이번 세션 (Option C) 성과

SYSTEM_NAVIGATOR.md의 자동 갱신 영역을 **3.5% → ~14%**로 확대. 14 Navigator 메타데이터를 자동 수집하여 4개 신규 섹션 자동 갱신.

### 신규 reader 함수 4개 (helpers.js)

1. **`readNavigatorsMeta(cwd)`**: 14 Navigator 메타 표 + 통계(줄/Mermaid/블럭/클릭) + Tier 커버리지
2. **`readPatternStats(cwd)`**: 5 패턴 적용 분포 + 패턴별 상세
3. **`readGapAnalysis(cwd)`**: Tier-C 미생성 + 비표준 메타 + 검증 통과 요약
4. **`readNavigatorDiagram(cwd)`**: 14 Navigator를 5 패턴 subgraph로 그룹화한 자동 Mermaid

### 보조 함수 3개

- `parseSkillMetaTable(navContent, skillName, skillFm)`: ### 스킬 메타 표 파싱 (구버전 파일럿 fallback 포함)
- `normalizeProcessType(rawType)`: 다양한 표기를 5 패턴 + 변형 2종으로 정규화
- `collectNavigatorsData(cwd)`: 14 Navigator 단일 진입점 (4 reader 공통 사용)

### navigator-updater.js 확장

- `watchMap`을 단일 마커 → 다중 마커 배열로 확장 (`markers: [...], labels: [...]`)
- 단일 트리거(`.agents/skills/*/Navigator.md` 변경)가 4 마커 동시 갱신
- 마커 누락 시 스킵 (점진적 도입 안전)
- 안전 검증 (50% 임계값) 보존

### SYSTEM_NAVIGATOR.md 신규 4 섹션

| 섹션 | 마커 | 위치 |
|------|------|------|
| **§1.2 Navigator 시스템 체계도 (자동)** | `navigator-diagram` | 신규 |
| **§5.3 Navigator 카탈로그 (자동 집계)** | `navigators-meta` | 신규 |
| **§5.4 패턴 라이브러리 통계 (자동)** | `pattern-stats` | 신규 |
| **§9.0 자동 Gap 감지 (Navigator 검증)** | `gap-analysis` | 신규 |

### 통계 변화

| 항목 | Option C 이전 | Option C 이후 |
|------|--------------|--------------|
| SYSTEM_NAVIGATOR.md 줄수 | 4003 | **4244** (+241, +6%) |
| AUTO 마커 수 | 8 | **13** (+5, navigator 4 + 통계용 표 갱신) |
| 자동 갱신 영역 | 3.5% (~143줄) | **~14% (~600줄)** |
| helpers.js 줄수 | 1061 | **~1500** (신규 함수 7개 + 모듈 exports 7) |
| Reader 함수 수 | 6 | **10** (+4) |
| 모듈 exports | 22 | **29** (+7) |

### 검증 결과

- **회귀 0**: 기존 8 AUTO 마커 (skills-catalog/mcp-servers/commands/imprints/pre-tool-guard/bkit-scripts) 모두 보존
- **신규 4 마커 자동 채움**: navigators-meta(38행) + pattern-stats(7 패턴) + gap-analysis(검증 통과) + navigator-diagram(자동 Mermaid 5 subgraph)
- **훅 시뮬레이션 성공**:
  - Navigator.md 변경 → 4 마커 동시 갱신
  - SKILL.md 변경 → skills-catalog 단일 갱신 (회귀 0)
- **wiki-lint**: 0 issues
- **기존 콘텐츠 0 손실**: 9 Mermaid + 217 블럭 카드 + 갱신 이력 모두 그대로

### 14 Navigator 자동 분류 결과

| 패턴 | 적용 수 | 대표 |
|------|:------:|------|
| Linear Pipeline | 5 | PaperResearch, ServiceMaker, PromptKit, FileNameMaking, Mermaid_FlowChart |
| Operation Dispatcher | 2 | llm-wiki, harness-imprint |
| Track | 2 | HWPX_Master, DocKit |
| Branching + Linear | 2 | mdGuide, term-organizer |
| Branching + Phase | 1 | harness-architect |
| Conditional Step | 1 | VisualCapture |
| Phase + Recursive Loop | 1 | auto-error-recovery |

**참고**: 이전 세션 분류와 mdGuide가 "Branching + Linear"로 재분류됨 (이전: Linear Pipeline) -- 정확한 normalizeProcessType 매칭 결과

---

## 현재 시스템 상태 스냅샷

### Navigator 보유 (19개, Tier-S/A/B 100% + Tier-C 4/8)

| Tier | 보유 | 전체 | 비율 |
|:---:|:---:|:---:|:---:|
| S | 1 | 1 | 100% |
| A | 4 | 4 | 100% |
| B | 9 | 9 | 100% |
| C | 4 | 8 | **50%** |
| **합계** | **18** | **22** | **82%** |

(15 → 19로 +4 증가. Option E 세션 1 결과)

### SYSTEM_NAVIGATOR.md 자동화 인프라

- **AUTO 마커**: 8 → 13개 (+5)
- **Reader 함수**: 6 → 10개 (+4)
- **자동 갱신 영역**: 143줄 → ~600줄
- **navigator-updater.js**: 단일 마커 → 다중 마커 처리

### 각인 + 용어

- 각인: 21개 (IMP-001~021, IMP-021 NEW)
- 전문용어: 54개
- 위키 wiki-lint: 0 issues

### 미커밋 파일

- `.claude/hooks/navigator-updater-helpers.js` (신규 함수 7개 + exports 7)
- `.claude/hooks/navigator-updater.js` (watchMap 확장 + multi-marker 처리)
- `SYSTEM_NAVIGATOR.md` (신규 4 섹션 + AUTO 마커 4 + 회귀 0)
- `.harness/next-session.md` (이 파일 갱신)

---

## 다음 세션 작업 선택지

### 옵션 E 세션 2 (다음 권장): Tier-C 큰 것 + 중간 것

세션 1에서 4/8 완료. 남은 4개 중 큰 것 + 중간 것 우선.

**세션 2 권장 2개**:
- **zero-script-qa** (~1400줄, Linear Pipeline, 가장 큼)
- **development-pipeline** (~280줄, Linear Pipeline, 9 Phase)

**세션 3 권장 2개** (마지막):
- **code-review** (~300줄, Operation Dispatcher)
- **bkit-templates** (~360줄, Linear Pipeline)

세션 3 완료 후 Tier-C 8/8 = 100% (전체 22/22 = 100%) 달성 → 옵션 K (Tier-C Wiki 진화) 권장.

### 옵션 G: Wiki 진화 (Option C 결과 지식화)

llm-wiki Mode 3로 이번 작업을 위키화:
- "SYSTEM_NAVIGATOR Auto-Aggregation" 신규 concept
- 260411_Option_C_Auto_Aggregation source
- Navigator_Pattern_Library 통계 자동화 명시

### 옵션 I: 표준화 마이그레이션 (NEW)

harness-architect, llm-wiki를 ### 스킬 메타 표 구조로 전환 → PILOT_PATTERNS hardcoded fallback 제거. helpers.js 단순화 (~30분).

### 옵션 J: README/CHANGELOG 자동 집계 (NEW)

Auto-Aggregation 패턴 재사용. README.md가 하위 모듈 메타데이터를 자동 수집하도록 multi-marker 적용 (~60분).

### 참고: 완료된 옵션

- **Option D** (commit 안정화)
- **Option B** (scaffold 고도화 + IMP-019/020)
- **Option A 세션 1-3** (Tier-B 9/9)
- **Option F** (Wiki 진화 -- Tier-B 100% 마일스톤)
- **Option C** (SYSTEM_NAVIGATOR.md 자동 재생성)
- **Option G** (Wiki 진화 -- Option C 결과 지식화)
- **Option H** (IMP-021 공식 기록)
- **Option E 세션 1** (Tier-C 4개: btw/plan-plus/bkit-rules/pdca) ← 이번 세션

---

## Warm Boot 체크리스트 (에이전트 자동 수행)

### 1. 자동 훅
- SessionStart 훅이 `active-imprints.md` 갱신 (20개 각인 중 상위 10개 로드)

### 2. 맥락 복원 Read
1. **이 파일** (`.harness/next-session.md`) -- **첫 번째**
2. `docs/LogManagement/1st_Log.md` (시간순 대시보드)
3. `SYSTEM_NAVIGATOR.md` §5.3 Navigator 카탈로그 (자동 집계 결과 확인)
4. `001_Wiki_AI/500_Technology/concepts/Navigator_Pattern_Library.md`

### 3. Git 상태 확인
```bash
git status --short
git log --oneline -5
```

### 4. SYSTEM_NAVIGATOR.md 확인
```bash
wc -l SYSTEM_NAVIGATOR.md
grep -c "AUTO:.*:START" SYSTEM_NAVIGATOR.md
```

### 5. navigator-updater.js 동작 확인 (선택)
```bash
echo '{"tool_input":{"file_path":".agents/skills/term-organizer/term-organizer_Navigator.md"}}' | node .claude/hooks/navigator-updater.js
```

---

## 다음 세션 시작 명령어 제안

```
세션 재개. .harness/next-session.md 읽고 옵션 E (Tier-C 확장) 시작해줘.
```

또는 다른 옵션:

```
세션 재개. 옵션 G (Wiki 진화 -- Option C 결과 지식화) 시작해줘.
세션 재개. 옵션 H (IMP-021 공식 기록) 처리해줘.
```

---

## Option C 핵심 기술 노트

### multi-marker 트리거 처리

`navigator-updater.js`가 단일 트리거(`Navigator.md` 변경)로 4 마커를 동시 갱신할 수 있도록 확장:
- 기존: `marker: 'X'` 단일 필드
- 신규: `markers: ['A', 'B', 'C', 'D'], labels: [...]` 배열
- 마커별 순차 처리 + 누적 변경 → 단일 atomicWriteWithBackup

### 구버전 파일럿 fallback

harness-architect, llm-wiki는 `### 스킬 메타` 섹션이 없는 구버전 구조:
- `parseSkillMetaTable`이 hardcoded fallback 사용 (PILOT_PATTERNS)
- 향후 두 파일럿을 표준 메타 표로 마이그레이션 권장

### 자동 정규식 분류

`normalizeProcessType` 함수가 자유 형식 표기를 5 패턴 + 변형 2종으로 정규화:
- "Linear Pipeline (5-Step + Trigger 분기)" → "Linear Pipeline"
- "Operation Dispatcher (7 ops + 2 훅)" → "Operation Dispatcher"
- "Phase + Recursive Loop" → "Phase + Recursive Loop"

---

## 세션 간 연속성 보장

- 플래닝 문서: `C:\Users\pyu42\.claude\plans\noble-booping-peach.md`
- 각인: 20개 (IMP-001~020)
- 이 파일: `.harness/next-session.md` (이번 세션 갱신 완료)
- Navigator 자동화 인프라 확대 (8 → 13 AUTO 마커, 6 → 10 reader)

**다음 세션 종료 시에도 이 파일을 최신화할 것. (IMP-018)**
