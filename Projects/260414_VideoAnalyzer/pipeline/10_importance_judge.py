"""
VideoAnalyzer Pipeline - Stage 3C-2: Claude 시각 판정 (Pass 2)
Pass 1 사전 분석 결과를 참고하여, Claude가 각 장면의 대표 프레임을
직접 보고 이미지 중요도를 최종 판정한다.

이 스크립트는 판정 대상 목록 + 판정 기준을 출력하는 가이드 프레임워크이다.
실제 판정은 Claude Code 런타임에서 수행되며, 판정 결과를 scene_NNN.json에 기록한다.

사용법:
  1. python 10_importance_judge.py          -- 판정 대상 목록 출력
  2. Claude가 각 프레임을 Read로 분석하고 판정
  3. python 10_importance_judge.py --apply   -- 판정 결과를 scene_NNN.json에 반영
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


def load_prefilter(analysis_dir: Path) -> dict | None:
    """Pass 1 사전 분석 결과를 로드한다."""
    prefilter_path = analysis_dir / "prefilter.json"
    if not prefilter_path.exists():
        return None
    with open(prefilter_path, encoding="utf-8") as f:
        return json.load(f)


def print_rules_summary(rules: dict) -> None:
    """적용할 규칙을 요약 출력한다."""
    print("\n[적용 규칙]")
    print("  -- 제외 규칙 (이미지 불필요) --")
    for r in rules["exclude_rules"]:
        print(f"    {r['id']}: {r['name']} -- {r['description']}")
    print("  -- 포함 규칙 (이미지 필수) --")
    for r in rules["include_rules"]:
        print(f"    {r['id']}: {r['name']} -- {r['description']}")


def generate_judge_targets(video_stem: str, analysis_base: Path,
                           frames_base: Path, rules: dict) -> None:
    """단일 영상의 판정 대상 목록과 가이드를 출력한다."""
    analysis_dir = analysis_base / video_stem
    frames_dir = frames_base / video_stem
    judge_path = analysis_dir / "judge_targets.json"

    if judge_path.exists():
        print(f"  이미 판정 대상 생성 완료. 건너뜁니다.")
        return

    prefilter = load_prefilter(analysis_dir)
    if prefilter is None:
        print(f"  prefilter.json 없음. Stage 3C-1을 먼저 실행하세요.")
        return

    # 사전 분석 결과를 scene_id로 인덱싱
    hint_map = {s["scene_id"]: s for s in prefilter["scenes"]}

    # 장면 파일 로드
    scene_files = sorted(analysis_dir.glob("scene_*.json"))

    targets = []
    for sf in scene_files:
        with open(sf, encoding="utf-8") as f:
            scene = json.load(f)

        sid = scene["scene_id"]
        hint_data = hint_map.get(sid, {})
        hint = hint_data.get("prefilter_hint", "NEEDS_VISUAL_CHECK")

        # 이미 판정 완료된 장면은 스킵
        if scene.get("importance_rule_version", 0) >= rules["version"]:
            continue

        frame_path = frames_dir / scene.get("frame_name", "")
        transcript = scene.get("text_analysis", {}).get("summary", "")

        target = {
            "scene_id": sid,
            "frame_name": scene.get("frame_name", ""),
            "frame_path": str(frame_path),
            "start_time": scene.get("start_time", 0),
            "prefilter_hint": hint,
            "deictic_count": hint_data.get("deictic_count", 0),
            "deictic_found": hint_data.get("deictic_found", []),
            "visual_keywords_found": hint_data.get("visual_keywords_found", []),
            "transcript_preview": transcript[:200],
            "judged": False,
            "is_important": None,
            "importance_reason": "",
        }
        targets.append(target)

    # 판정 대상 저장
    output = {
        "video_stem": video_stem,
        "rule_version": rules["version"],
        "total_targets": len(targets),
        "stats": {
            "LIKELY_IMPORTANT": sum(1 for t in targets if t["prefilter_hint"] == "LIKELY_IMPORTANT"),
            "NEEDS_VISUAL_CHECK": sum(1 for t in targets if t["prefilter_hint"] == "NEEDS_VISUAL_CHECK"),
            "LIKELY_SKIP": sum(1 for t in targets if t["prefilter_hint"] == "LIKELY_SKIP"),
        },
        "targets": targets,
    }

    with open(judge_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  판정 대상 생성: {len(targets)}개 장면")
    print(f"    LIKELY_IMPORTANT: {output['stats']['LIKELY_IMPORTANT']}개 (우선 분석)")
    print(f"    NEEDS_VISUAL_CHECK: {output['stats']['NEEDS_VISUAL_CHECK']}개 (이미지 확인 필요)")
    print(f"    LIKELY_SKIP: {output['stats']['LIKELY_SKIP']}개 (빠른 확인)")


def apply_judgments(video_stem: str, analysis_base: Path, rules: dict) -> None:
    """판정 결과를 scene_NNN.json에 반영한다."""
    analysis_dir = analysis_base / video_stem
    judge_path = analysis_dir / "judge_targets.json"

    if not judge_path.exists():
        print(f"  judge_targets.json 없음. 판정 대상을 먼저 생성하세요.")
        return

    with open(judge_path, encoding="utf-8") as f:
        judge_data = json.load(f)

    applied = 0
    skipped = 0

    for target in judge_data["targets"]:
        if not target.get("judged", False):
            skipped += 1
            continue

        sid = target["scene_id"]
        scene_path = analysis_dir / f"scene_{sid:03d}.json"
        if not scene_path.exists():
            continue

        with open(scene_path, encoding="utf-8") as f:
            scene = json.load(f)

        scene["is_important_frame"] = target["is_important"]
        scene["importance_reason"] = target["importance_reason"]
        scene["importance_rule_version"] = rules["version"]

        with open(scene_path, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=2)

        applied += 1

    print(f"  판정 반영: {applied}개 적용, {skipped}개 미판정")


def main():
    """Stage 3C-2: Claude 시각 판정 가이드."""
    config = load_config()
    analysis_base = get_path(config, "workspace_analysis")
    frames_base = get_path(config, "workspace_frames")

    # 규칙 파일 로드
    rules_path = Path(__file__).parent / "importance_rules.json"
    if not rules_path.exists():
        print("오류: importance_rules.json이 없습니다.")
        sys.exit(1)

    rules = load_rules(rules_path)

    # --apply 모드 확인
    apply_mode = "--apply" in sys.argv

    # 장면 파일이 존재하는 영상 서브디렉토리 탐색
    video_dirs = sorted(
        d for d in analysis_base.iterdir()
        if d.is_dir() and list(d.glob("scene_*.json"))
    )
    if not video_dirs:
        print("오류: 장면 분석 파일이 없습니다.")
        sys.exit(1)

    if apply_mode:
        print(f"\n=== Stage 3C-2: 판정 결과 반영 ===")
        for vdir in video_dirs:
            stem = vdir.name
            print(f"\n--- [{stem}] ---")
            apply_judgments(stem, analysis_base, rules)
    else:
        print(f"\n=== Stage 3C-2: Claude 시각 판정 대상 생성 ===")
        print_rules_summary(rules)
        print(f"\n영상 {len(video_dirs)}개 처리:")

        for vdir in video_dirs:
            stem = vdir.name
            print(f"\n--- [{stem}] ---")
            generate_judge_targets(stem, analysis_base, frames_base, rules)

        print(f"\n=== Stage 3C-2 전체 완료 ===")
        print()
        print("=" * 70)
        print("다음 단계: Claude Code에서 각 장면을 판정하세요.")
        print()
        print("  판정 방법:")
        print("  1. judge_targets.json의 각 target에 대해:")
        print("     - LIKELY_IMPORTANT: 프레임 Read -> include 규칙 확인 -> 판정")
        print("     - NEEDS_VISUAL_CHECK: 프레임 Read -> include/exclude 규칙 판단")
        print("     - LIKELY_SKIP: 트랜스크립트만으로 판단 가능하면 스킵,")
        print("                   불확실하면 프레임 Read")
        print("  2. judged=true, is_important=true/false, importance_reason 기입")
        print("  3. python 10_importance_judge.py --apply 로 scene_NNN.json 반영")
        print("=" * 70)


if __name__ == "__main__":
    main()
