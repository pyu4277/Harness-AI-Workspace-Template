# 아키텍처 결정 기록 (ADR) -- VideoAnalyzer

> 주요 아키텍처 결정을 기록한다. 새 결정 시 하단에 ADR-VA-NNN으로 추가.

---

## ADR-VA-001: 보고서 포맷 Markdown (.md)

**상태**: 폐기 (2026-04-15) -- ADR-VA-004로 대체
**컨텍스트**: LLM 학습 최적화 포맷 선택 필요.
**결정**: .md (Markdown). 모든 LLM이 네이티브로 읽고 이해하는 포맷.
**근거**: 구조적 헤딩, 코드 블록, Mermaid, base64 이미지 삽입 지원. Git 호환.

---

## ADR-VA-002: 이미지 삽입 base64 인라인

**상태**: 폐기 (2026-04-15) -- ADR-VA-005로 대체
**컨텍스트**: 보고서를 다른 환경에서 열어도 이미지가 깨지면 안 됨.
**결정**: `![desc](data:image/jpeg;base64,...)` 직접 삽입. 상대경로 참조 금지.
**근거**: 단일 파일 자기완결성, 복사/이동 시 깨짐 방지.

---

## ADR-VA-003: Whisper 폴백

**상태**: 채택 (2026-04-14)
**컨텍스트**: 일부 영상에 자막이 없음.
**결정**: 사용자 자막 우선, 없을 시 Whisper 자동 음성추출.
**근거**: 사용자 자막이 전문용어 정확도에서 항상 우위.

---

## ADR-VA-004: 보고서 포맷 HWPX 전환

**상태**: 채택 (2026-04-15) -- ADR-VA-001 대체
**컨텍스트**: 사용자가 한/글에서 보고서를 열어 편집/인쇄해야 함. Markdown은 이미지 삽입에 base64 한계.
**결정**: HWPX 형식 (python-hwpx v2.8). 텍스트는 python-hwpx, 이미지는 한/글 COM 2-Phase.
**근거**: 한국 대학/행정 환경에서 한/글이 표준 문서 도구. 이미지 직접 삽입 + AI 설명서 배치 가능.

---

## ADR-VA-005: 2-Phase COM 이미지 삽입

**상태**: 채택 (2026-04-15) -- ADR-VA-002 대체
**컨텍스트**: python-hwpx의 `add_image()`로 삽입한 이미지는 한/글에서 열기 실패. OWPML XML 직접 빌드, `[Content_Types].xml` 주입, sizeoption 파라미터 등 7가지 접근 모두 실패.
**결정**: 2-Phase 방식. Phase 1: python-hwpx 텍스트 전용 HWPX + `<<IMG:파일명>>` 마커. Phase 2: 한/글 COM (`HWPFrame.HwpObject.InsertPicture`)으로 마커를 실제 이미지로 교체.
**근거**: COM 자동화가 한/글과 호환되는 유일한 이미지 삽입 방법 (HWPX_Master 스킬 실증).
**참조**: `HWPX_Master/references/hwpx-format.md` "이미지 삽입 (2-Phase COM 방식)" 섹션.

---

## ADR-VA-006: HWP 96 DPI 기반 이미지 크기 제어

**상태**: 채택 (2026-04-15)
**컨텍스트**: `InsertPicture`의 Width/Height 파라미터, sizeoption(0/2/3), JPEG DPI 메타데이터 모두 이미지 표시 크기를 제어하지 못함. 한/글은 내부 96 DPI 고정으로 픽셀 크기만 참조.
**결정**: 이미지를 본문 폭(150mm)에 맞는 567px로 리사이즈 후 삽입. 공식: `px = body_mm / 25.4 * 96`.
**근거**: A4 기본 여백 좌우 30mm -> 본문 폭 150mm = 42520 HWPU. 1px = 75 HWPU (7200/96). HWPX XML 내 `orgSz` 검증으로 확인.
