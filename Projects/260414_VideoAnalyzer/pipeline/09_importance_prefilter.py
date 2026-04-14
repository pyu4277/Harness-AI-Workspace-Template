"""
VideoAnalyzer Pipeline - Stage 3C-1: 텍스트 사전 분석 (Pass 1)
장면별 트랜스크립트를 분석하여 이미지 중요도 사전 힌트를 생성한다.
LLM 없이 키워드 기반으로 빠르게 분류한다.

규칙 파일: pipeline/importance_rules.json (진화 가능)
"""
import json
import sys
from pathlib import Path

from config_loader import load_config
from path_utils import get_path, ensure_dir


def load_rules(rules_path: Path) -> dict:
    """중요도 판별 규칙을 로드한다."""
    with open(rules_path, encoding="utf-8") as f:
        return json.load(f)


def count_keywords(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    """텍스트에서 키워드 출현 횟수와 매칭된 키워드 목록을 반환한다."""
    found = []
    count = 0
    for kw in keywords:
        occurrences = text.count(kw)
        if occurrences > 0:
            count += occurrences
            found.append(kw)
    return count, found


def classify_scene(transcript: str, settings: dict) -> dict:
    """단일 장면의 트랜스크립트를 분석하여 사전 힌트를 생성한다."""
    deictic_pronouns = settings["deictic_pronouns"]
    visual_keywords = settings["visual_keywords"]
    deictic_threshold = settings["deictic_threshold"]
    short_threshold = settings["short_transcript_threshold"]

    deictic_count, deictic_found = count_keywords(transcript, deictic_pronouns)
    visual_count, visual_found = count_keywords(transcript, visual_keywords)
    transcript_length = len(transcript)

    # 힌트 판정 로직
    if deictic_count >= deictic_threshold or visual_count > 0:
        hint = "LIKELY_IMPORTANT"
    elif transcript_length < short_threshold:
        hint = "LIKELY_SKIP"
    else:
        hint = "NEEDS_VISUAL_CHECK"

    return {
        "deictic_count": deictic_count,
        "deictic_found": deictic_found,
        "visual_keyword_count": visual_count,
        "visual_keywords_found": visual_found,
        "transcript_length": transcript_length,
        "prefilter_hint": hint,
    }


def process_single_video(video_stem: str, analysis_base: Path, rules: dict) -> None:
    """단일 영상의 모든 장면에 텍스트 사전 분석을 수행한다."""
    analysis_dir = analysis_base / video_stem
    prefilter_path = analysis_dir / "prefilter.json"

    if prefilter_path.exists():
        print(f"  이미 사전 분석 완료. 건너뜁니다.")
        return

    if not analysis_dir.exists():
        print(f"  분석 디렉토리 없음. Stage 3B를 먼저 실행하세요.")
        return

    # 장면 파일 로드
    scene_files = sorted(analysis_dir.glob("scene_*.json"))
    if not scene_files:
        print(f"  장면 파일 없음. Stage 3B를 먼저 실행하세요.")
        return

    settings = rules["prefilter_settings"]
    results = []
    stats = {"LIKELY_IMPORTANT": 0, "NEEDS_VISUAL_CHECK": 0, "LIKELY_SKIP": 0}

    for sf in scene_files:
        with open(sf, encoding="utf-8") as f:
            scene = json.load(f)

        transcript = scene.get("text_analysis", {}).get("summary", "")
        classification = classify_scene(transcript, settings)
        classification["scene_id"] = scene["scene_id"]
        classification["frame_name"] = scene.get("frame_name", "")

        results.append(classification)
        stats[classification["prefilter_hint"]] += 1

    # 결과 저장
    output = {
        "video_stem": video_stem,
        "rule_version": rules["version"],
        "total_scenes": len(results),
        "stats": stats,
        "scenes": results,
    }

    with open(prefilter_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  사전 분석 완료: {len(results)}개 장면")
    print(f"    LIKELY_IMPORTANT: {stats['LIKELY_IMPORTANT']}개")
    print(f"    NEEDS_VISUAL_CHECK: {stats['NEEDS_VISUAL_CHECK']}개")
    print(f"    LIKELY_SKIP: {stats['LIKELY_SKIP']}개")


def main():
    """Stage 3C-1: 모든 영상의 텍스트 사전 분석."""
    config = load_config()
    analysis_base = get_path(config, "workspace_analysis")

    # 규칙 파일 로드
    rules_path = Path(__file__).parent / "importance_rules.json"
    if not rules_path.exists():
        print("오류: importance_rules.json이 없습니다.")
        sys.exit(1)

    rules = load_rules(rules_path)
    print(f"규칙 버전: {rules['version']}")

    # 장면 파일이 존재하는 영상 서브디렉토리 탐색
    video_dirs = sorted(
        d for d in analysis_base.iterdir()
        if d.is_dir() and list(d.glob("scene_*.json"))
    )
    if not video_dirs:
        print("오류: 장면 분석 파일이 없습니다. Stage 3B를 먼저 실행하세요.")
        sys.exit(1)

    print(f"\n=== Stage 3C-1: 텍스트 사전 분석 (Pass 1) ===")
    print(f"영상 {len(video_dirs)}개 처리:")

    for vdir in video_dirs:
        stem = vdir.name
        print(f"\n--- [{stem}] ---")
        process_single_video(stem, analysis_base, rules)

    print(f"\n=== Stage 3C-1 전체 완료 ===")


if __name__ == "__main__":
    main()
