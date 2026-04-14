"""
VideoAnalyzer Pipeline - Stage 4: 레퍼런스 수집 가이드
분석 결과에서 감지된 레퍼런스 니즈를 수집한다.
실제 수집은 Claude Code 런타임에서 MCP(exa/firecrawl)로 수행된다.
"""
import json
import sys
from pathlib import Path

from config_loader import load_config
from path_utils import get_path, ensure_dir


def collect_reference_needs(analysis_dir: Path) -> list[dict]:
    """모든 장면 분석 결과에서 레퍼런스 니즈를 수집한다."""
    needs = []
    seen_keywords = set()

    for scene_file in sorted(analysis_dir.glob("scene_*.json")):
        with open(scene_file, encoding="utf-8") as f:
            scene = json.load(f)

        for keyword in scene.get("reference_needs", []):
            if keyword not in seen_keywords:
                seen_keywords.add(keyword)
                needs.append({
                    "keyword": keyword,
                    "source_scene": scene["scene_id"],
                    "collected": False,
                    "verified": False,
                })

    return needs


def main():
    """Stage 4: 레퍼런스 니즈 수집 + 검색 가이드."""
    config = load_config()

    analysis_dir = get_path(config, "workspace_analysis")
    research_dir = get_path(config, "workspace_research")
    ensure_dir(research_dir)

    print(f"\n=== Stage 4: 레퍼런스 수집 ===")

    # 레퍼런스 니즈 수집
    needs = collect_reference_needs(analysis_dir)

    if not needs:
        print("레퍼런스 니즈가 없습니다. Stage 5로 진행하세요.")
        # 빈 목록 저장
        needs_path = research_dir / "reference_needs.json"
        with open(needs_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    print(f"레퍼런스 니즈 {len(needs)}건 감지:")
    for n in needs:
        print(f"  - [{n['source_scene']:3d}] {n['keyword']}")

    # 니즈 목록 저장
    needs_path = research_dir / "reference_needs.json"
    with open(needs_path, "w", encoding="utf-8") as f:
        json.dump(needs, f, ensure_ascii=False, indent=2)

    print(f"\n니즈 목록 저장: {needs_path}")
    print()
    print("=" * 60)
    print("다음 단계: Claude Code에서 레퍼런스를 수집하세요.")
    print("  1. exa-web-search MCP로 시맨틱 검색")
    print("  2. firecrawl MCP로 페이지 스크래핑")
    print("  3. LLM으로 품질 검증 (관련도 80%+, 신뢰도 확인)")
    print("  4. 검증 통과 자료만 research/ref_NNN.json으로 저장")
    print("  5. 검증 실패 자료는 폐기 (보고서 통합 금지)")
    print("=" * 60)


if __name__ == "__main__":
    main()
