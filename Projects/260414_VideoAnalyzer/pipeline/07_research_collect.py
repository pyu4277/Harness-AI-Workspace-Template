"""
VideoAnalyzer Pipeline - Stage 4: 레퍼런스 수집 가이드
분석 결과에서 감지된 레퍼런스 니즈를 수집한다.
실제 수집은 Claude Code 런타임에서 MCP(exa/firecrawl)로 수행된다.

개량 v2: 다중 영상 서브디렉토리 지원
"""
import json
import sys
from pathlib import Path

from config_loader import load_config
from path_utils import get_path, ensure_dir


def collect_reference_needs(analysis_dir: Path) -> list[dict]:
    """장면 분석 결과에서 레퍼런스 니즈를 수집한다."""
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


def process_single_video(video_stem: str, analysis_base: Path, research_base: Path) -> None:
    """단일 영상의 레퍼런스 니즈를 수집한다."""
    analysis_dir = analysis_base / video_stem
    research_dir = research_base / video_stem
    ensure_dir(research_dir)

    needs_path = research_dir / "reference_needs.json"
    if needs_path.exists():
        print(f"  이미 니즈 목록 존재. 건너뜁니다.")
        return

    if not analysis_dir.exists() or not list(analysis_dir.glob("scene_*.json")):
        print(f"  분석 결과 없음. Stage 3을 먼저 실행하세요.")
        return

    needs = collect_reference_needs(analysis_dir)

    with open(needs_path, "w", encoding="utf-8") as f:
        json.dump(needs, f, ensure_ascii=False, indent=2)

    if not needs:
        print(f"  레퍼런스 니즈 없음. Stage 5로 진행 가능.")
    else:
        print(f"  레퍼런스 니즈 {len(needs)}건 감지:")
        for n in needs:
            print(f"    - [{n['source_scene']:3d}] {n['keyword']}")


def main():
    """Stage 4: 모든 영상의 레퍼런스 니즈 수집."""
    config = load_config()

    analysis_base = get_path(config, "workspace_analysis")
    research_base = get_path(config, "workspace_research")

    # 분석 결과가 존재하는 영상 서브디렉토리 탐색
    if not analysis_base.exists():
        print("오류: 분석 결과가 없습니다. Stage 3을 먼저 실행하세요.")
        sys.exit(1)

    video_dirs = sorted(
        d for d in analysis_base.iterdir()
        if d.is_dir() and list(d.glob("scene_*.json"))
    )
    if not video_dirs:
        print("오류: 분석 결과가 없습니다. Stage 3을 먼저 실행하세요.")
        sys.exit(1)

    print(f"\n=== Stage 4: 레퍼런스 수집 ===")
    print(f"영상 {len(video_dirs)}개 처리:")

    for vdir in video_dirs:
        stem = vdir.name
        print(f"\n--- [{stem}] ---")
        process_single_video(stem, analysis_base, research_base)

    print(f"\n=== Stage 4 전체 완료 ===")
    print()
    print("=" * 60)
    print("다음 단계: Claude Code에서 레퍼런스를 수집하세요.")
    print("  1. exa-web-search MCP로 시맨틱 검색")
    print("  2. firecrawl MCP로 페이지 스크래핑")
    print("  3. LLM으로 품질 검증 (관련도 80%+, 신뢰도 확인)")
    print("  4. 검증 통과 자료만 research/{stem}/ref_NNN.json으로 저장")
    print("  5. 검증 실패 자료는 폐기 (보고서 통합 금지)")
    print("=" * 60)


if __name__ == "__main__":
    main()
