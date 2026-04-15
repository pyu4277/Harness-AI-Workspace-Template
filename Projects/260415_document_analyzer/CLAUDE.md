# CLAUDE.md — 260415_document_analyzer

> 본 프로젝트는 상위 `005_AI_Project/CLAUDE.md`를 상속하고, 아래 규칙을 추가 강제한다.

## HWPX 산출 — 보고서 작업의 마지막 단계 (IMP-046)

- `Output/Reports/*.md` 또는 `Output/Errors/*.md`를 신규 작성·수정한 경우, **동일 stem의 HWPX가 `Output/Reports_HWPX/`·`Output/Errors_HWPX/`에 존재하고 mtime이 MD 이상**이어야 한다.
- 미충족 시 "보고서 완료" 보고 금지. 하네스 위반으로 간주.
- 변환 표준 명령:

```bash
python src/renderers/md_to_hwpx.py \
  --md   Output/Reports \
  --out  Output/Reports_HWPX \
  --mmd-dir .bkit_runtime/mmd \
  --png-dir .bkit_runtime/png

python src/renderers/md_to_hwpx.py \
  --md   Output/Errors \
  --out  Output/Errors_HWPX \
  --mmd-dir .bkit_runtime/mmd \
  --png-dir .bkit_runtime/png
```

- 검증: `[OK] ... (images: N/N)` 로그에서 분자 = 분모 (Mermaid 100% 삽입). 미일치 시 정지·보고.
- 예외: `_v1_backup/`, `docs/`, `README.md`는 면제.

## v2 서술형 표준 (IMP-044, IMP-045)

- 본문은 서술형 한국어 단락. 페이지는 인쇄 페이지 우선(`p.N (seq M)`).
- 직독 검증 후만 사실 단정. 미검증은 "확인 불가"로 명기.
- 상세: `docs/report_format_v2.md`.

## 완료 체크리스트 (본 분석기 추가 항목)

상위 CLAUDE.md 0~4번에 더해:

5. **HWPX 산출 검증**: 신규/수정된 보고서 MD에 대응하는 HWPX 존재 + mtime ≥ MD + Mermaid 이미지 N/N 일치.
