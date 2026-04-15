"""Phase 4-2: build 4-way mapping index.

Standard schema: format (작성서식) defines required sections.
Map plan / evidence / pres / indicator anchors to format sections.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
RUNTIME = PROJECT / ".bkit_runtime"
PAGES_DIR = RUNTIME / "pages"

# Format-defined required sections (manually curated from headings.json + format inspection).
FORMAT_SECTIONS = [
    {"sec_id": "Ⅰ.1.1", "title": "대학의 AI·DX 교육여건 분석", "format_pages": [2], "area": "사업추진목표"},
    {"sec_id": "Ⅰ.1.2", "title": "대학의 AI·DX 특성화 방향", "format_pages": [2], "area": "사업추진목표"},
    {"sec_id": "Ⅰ.2.1", "title": "사업추진 목표", "format_pages": [3], "area": "사업추진목표"},
    {"sec_id": "Ⅰ.2.2", "title": "학습자의 AID 목표역량을 고려한 AI·DX 특화 모델", "format_pages": [3], "area": "사업추진목표"},
    {"sec_id": "Ⅱ.총괄표", "title": "사업추진 계획 총괄표", "format_pages": [5, 6], "area": "사업추진실적및계획"},
    {"sec_id": "Ⅱ.1", "title": "AI·DX 교육기반 구축을 위한 인프라 및 추진체계", "format_pages": [7], "area": "사업추진실적및계획"},
    {"sec_id": "Ⅱ.2.1", "title": "AI·DX 교육과정 개발·운영체제 구축·운영 실적 및 계획", "format_pages": [8, 9], "area": "사업추진실적및계획"},
    {"sec_id": "Ⅱ.2.2", "title": "학습성과관리 실적 및 계획", "format_pages": [10], "area": "사업추진실적및계획"},
    {"sec_id": "Ⅱ.3.1", "title": "AI·DX 기반 교수학습 혁신 실적 및 계획", "format_pages": [11], "area": "사업추진실적및계획"},
    {"sec_id": "Ⅱ.3.2", "title": "AI·DX 기반 교직원 역량강화 실적 및 계획", "format_pages": [12], "area": "사업추진실적및계획"},
    {"sec_id": "Ⅱ.4.1", "title": "학습자 지원을 위한 AI·DX 교육환경 개선 실적 및 계획", "format_pages": [13], "area": "사업추진실적및계획"},
    {"sec_id": "Ⅱ.4.2", "title": "AI·DX 교육을 위한 산학연계 실적 및 계획", "format_pages": [14], "area": "사업추진실적및계획"},
    {"sec_id": "Ⅲ.1.1", "title": "AI·DX 추진 거버넌스 총괄 체계", "format_pages": [16], "area": "사업추진체계및성과관리"},
    {"sec_id": "Ⅲ.1.2", "title": "AI·DX 거버넌스 구축·운영 방안 및 거버넌스별 주요 기능", "format_pages": [17], "area": "사업추진체계및성과관리"},
    {"sec_id": "Ⅲ.2.1.1", "title": "핵심성과지표 총괄표", "format_pages": [18], "area": "사업추진체계및성과관리"},
    {"sec_id": "Ⅲ.2.1.2", "title": "핵심성과지표 설정 및 세부계획", "format_pages": [19, 20, 21, 22, 23, 24, 25, 26], "area": "사업추진체계및성과관리"},
    {"sec_id": "Ⅲ.2.2", "title": "자율성과지표 설정 및 달성 목표", "format_pages": [27, 28, 29], "area": "사업추진체계및성과관리"},
    {"sec_id": "Ⅲ.3.1", "title": "성과관리 계획", "format_pages": [30], "area": "사업추진체계및성과관리"},
    {"sec_id": "Ⅲ.3.2", "title": "성과 공유·확산 계획", "format_pages": [30], "area": "사업추진체계및성과관리"},
    {"sec_id": "Ⅳ.1.1", "title": "대학의 AI·DX 재정투자 전략", "format_pages": [32, 33], "area": "재정집행계획"},
    {"sec_id": "Ⅳ.1.2.1", "title": "총 사업비 구성", "format_pages": [35], "area": "재정집행계획"},
    {"sec_id": "Ⅳ.1.2.2", "title": "1차년도(2026년) 비목별 집행 계획", "format_pages": [36, 37], "area": "재정집행계획"},
    {"sec_id": "Ⅳ.1.2.3", "title": "1차년도(2026년) 사업비 구성", "format_pages": [38, 39, 40], "area": "재정집행계획"},
]

# 4 areas × 10 items × 100 points (from indicator_p0001.png)
INDICATORS = [
    {"area": "사업추진목표", "area_pts": 15, "item": "대학의 여건 및 AI·DX 특성화 방향의 적절성", "pts": 7, "covers": ["Ⅰ.1.1", "Ⅰ.1.2"]},
    {"area": "사업추진목표", "area_pts": 15, "item": "사업추진 목표 및 학습자 목표의 AI·DX 역량 타당성", "pts": 8, "covers": ["Ⅰ.2.1", "Ⅰ.2.2"]},
    {"area": "사업추진실적및계획", "area_pts": 50, "item": "AI·DX 교육기반 구축을 위한 인프라 및 추진체계의 적절성", "pts": 10, "covers": ["Ⅱ.1"]},
    {"area": "사업추진실적및계획", "area_pts": 50, "item": "AI·DX 교육과정 개발·운영체제 구축·운영 실적 및 계획의 우수성", "pts": 20, "covers": ["Ⅱ.2.1", "Ⅱ.2.2"]},
    {"area": "사업추진실적및계획", "area_pts": 50, "item": "AI·DX 기반 교수학습 혁신 및 교직원 역량강화 실적 및 계획의 우수성", "pts": 10, "covers": ["Ⅱ.3.1", "Ⅱ.3.2"]},
    {"area": "사업추진실적및계획", "area_pts": 50, "item": "학습자 지원을 위한 교육환경 개선 및 산학연계 실적 및 계획의 우수성", "pts": 10, "covers": ["Ⅱ.4.1", "Ⅱ.4.2"]},
    {"area": "사업추진체계및성과관리", "area_pts": 20, "item": "사업추진체계의 적절성", "pts": 5, "covers": ["Ⅲ.1.1", "Ⅲ.1.2"]},
    {"area": "사업추진체계및성과관리", "area_pts": 20, "item": "성과지표 설정의 적절성(공통지표 및 자율지표)", "pts": 7, "covers": ["Ⅲ.2.1.1", "Ⅲ.2.1.2", "Ⅲ.2.2"]},
    {"area": "사업추진체계및성과관리", "area_pts": 20, "item": "성과 공유·확산 계획의 우수성 및 지속가능성", "pts": 8, "covers": ["Ⅲ.3.1", "Ⅲ.3.2"]},
    {"area": "재정집행계획", "area_pts": 15, "item": "재정집행 계획의 적절성", "pts": 15, "covers": ["Ⅳ.1.1", "Ⅳ.1.2.1", "Ⅳ.1.2.2", "Ⅳ.1.2.3"]},
]


def _norm_title(s: str) -> str:
    return re.sub(r"[\s·ㆍ･ž]+", "", s).lower()


def _find_plan_pages_for_section(plan_headings: list, sec: dict) -> list[int]:
    """Map plan pages to format section by title fuzzy match."""
    target = _norm_title(sec["title"])
    out = set()
    for entry in plan_headings:
        for h in entry["headings"]:
            if h["type"] == "deep" and _norm_title(h["title"]) == target:
                out.add(entry["page"])
    if not out:
        # Substring fuzzy match
        for entry in plan_headings:
            for h in entry["headings"]:
                ht = _norm_title(h["title"])
                if ht and (target[:12] in ht or ht[:12] in target):
                    out.add(entry["page"])
    return sorted(out)


def _find_evidence_pages_for_section(evidence_headings: list, sec_id: str, sec_title: str) -> list[int]:
    """Evidence headings carry pattern like 'Ⅱ.2.1.1 ... P.18'."""
    out = set()
    sec_id_no_roman = sec_id.split(".", 1)[1] if "." in sec_id else sec_id
    target = _norm_title(sec_title)
    for entry in evidence_headings:
        joined = " ".join(h["title"] for h in entry["headings"])
        joined_n = _norm_title(joined)
        if (sec_id_no_roman in joined or sec_id in joined) or (target and target[:10] in joined_n):
            out.add(entry["page"])
    return sorted(out)


def _detect_evidence_ref_inconsistency(plan_headings: list) -> list[dict]:
    """플랜 단원에 [증빙 P,X] vs [증빙 P.X] 표기 불일치 검출."""
    issues = []
    for entry in plan_headings:
        for h in entry["headings"]:
            if "증빙" in h["title"]:
                if "P,1" in h["title"] or re.search(r"P\s*,\s*\d", h["title"]):
                    issues.append({"page": entry["page"], "form": "P,N (콤마)", "raw": h["title"][:100]})
                elif re.search(r"P\.\s*\d", h["title"]):
                    issues.append({"page": entry["page"], "form": "P.N (점)", "raw": h["title"][:100]})
    return issues


def main() -> int:
    headings = json.loads((RUNTIME / "headings.json").read_text(encoding="utf-8"))
    plan_h = headings["plan"]
    evi_h = headings["evidence"]

    mapping = []
    for sec in FORMAT_SECTIONS:
        plan_pages = _find_plan_pages_for_section(plan_h, sec)
        evi_pages = _find_evidence_pages_for_section(evi_h, sec["sec_id"], sec["title"])
        mapping.append({
            **sec,
            "plan_pages": plan_pages,
            "evidence_pages": evi_pages,
            "plan_present": bool(plan_pages),
            "evidence_present": bool(evi_pages),
        })

    indicator_map = []
    for ind in INDICATORS:
        plan_total = []
        evi_total = []
        for cov in ind["covers"]:
            for m in mapping:
                if m["sec_id"] == cov:
                    plan_total.extend(m["plan_pages"])
                    evi_total.extend(m["evidence_pages"])
        indicator_map.append({
            **ind,
            "plan_pages": sorted(set(plan_total)),
            "evidence_pages": sorted(set(evi_total)),
        })

    inconsistencies = _detect_evidence_ref_inconsistency(plan_h)

    out = {
        "schema_source": "format (작성서식)",
        "section_count": len(FORMAT_SECTIONS),
        "indicator_count": len(INDICATORS),
        "indicator_total_pts": sum(i["pts"] for i in INDICATORS),
        "section_4way_mapping": mapping,
        "indicator_to_pages": indicator_map,
        "early_findings": {
            "evidence_ref_format_inconsistency": inconsistencies,
            "missing_plan_sections": [m["sec_id"] for m in mapping if not m["plan_present"]],
            "missing_evidence_sections": [m["sec_id"] for m in mapping if not m["evidence_present"]],
        },
    }
    (RUNTIME / "mapping_4way.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[OK] sections={len(mapping)}, missing_plan={len(out['early_findings']['missing_plan_sections'])}, missing_evi={len(out['early_findings']['missing_evidence_sections'])}, ref_inconsistencies={len(inconsistencies)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
