"""
VideoAnalyzer Pipeline - Stage 3C-3: 자동 중요도 판정
텍스트 사전 분석(Pass 1) + OpenCV 시각 분류(Pass 1.5) 결과를 결합하여
is_important_frame을 자동 판정하고 scene_NNN.json에 바로 반영한다.

판정 매트릭스:
  CONTENT_RICH + LIKELY_IMPORTANT   -> True  (확실한 콘텐츠 + 지시대명사)
  CONTENT_RICH + NEEDS_VISUAL_CHECK -> True  (콘텐츠 있음, EX-03 가능성은 있으나 안전하게 포함)
  CONTENT_RICH + LIKELY_SKIP        -> True  (콘텐츠 있으면 대본 짧아도 포함)
  MIXED + LIKELY_IMPORTANT          -> True  (화면공유+웹캠, 지시대명사 있으면 콘텐츠 중심)
  MIXED + NEEDS_VISUAL_CHECK        -> True  (MIXED는 콘텐츠 포함 가능성 높음)
  MIXED + LIKELY_SKIP               -> False (MIXED지만 대본 내용 없으면 제외)
  TALKING_HEAD + *                  -> False (토킹 헤드는 대본만으로 충분)
  SPARSE_SCREEN + *                 -> False (빈 화면은 제외)
"""
import json
import sys
from pathlib import Path

from config_loader import load_config
from path_utils import get_path


# 판정 매트릭스: (visual_class, prefilter_hint) -> (is_important, reason)
DECISION_MATRIX = {
    ("CONTENT_RICH", "LIKELY_IMPORTANT"):   (True,  "IN-01/02: 콘텐츠 프레임 + 지시대명사/시각키워드"),
    ("CONTENT_RICH", "NEEDS_VISUAL_CHECK"): (True,  "IN-02: 콘텐츠 프레임 (시각 정보 포함)"),
    ("CONTENT_RICH", "LIKELY_SKIP"):        (True,  "IN-02: 콘텐츠 프레임 (대본 짧지만 시각 정보 포함)"),
    ("MIXED", "LIKELY_IMPORTANT"):          (True,  "IN-01/02: 화면공유+웹캠, 지시대명사/시각키워드"),
    ("MIXED", "NEEDS_VISUAL_CHECK"):        (True,  "IN-02: 화면공유 레이아웃 (콘텐츠 포함 가능성)"),
    ("MIXED", "LIKELY_SKIP"):               (False, "EX-01: 화면공유+웹캠이지만 대본 내용 없음"),
    ("TALKING_HEAD", "LIKELY_IMPORTANT"):    (False, "EX-01: 토킹 헤드 (대본에 지시대명사 있으나 화면은 얼굴)"),
    ("TALKING_HEAD", "NEEDS_VISUAL_CHECK"):  (False, "EX-01: 토킹 헤드"),
    ("TALKING_HEAD", "LIKELY_SKIP"):         (False, "EX-01: 토킹 헤드 + 대본 내용 없음"),
    ("SPARSE_SCREEN", "LIKELY_IMPORTANT"):   (False, "EX-02: 빈 화면"),
    ("SPARSE_SCREEN", "NEEDS_VISUAL_CHECK"): (False, "EX-02: 빈 화면"),
    ("SPARSE_SCREEN", "LIKELY_SKIP"):        (False, "EX-02: 빈 화면 + 대본 내용 없음"),
    ("ERROR", "LIKELY_IMPORTANT"):           (False, "ERROR: 프레임 로드 실패"),
    ("ERROR", "NEEDS_VISUAL_CHECK"):         (False, "ERROR: 프레임 로드 실패"),
    ("ERROR", "LIKELY_SKIP"):                (False, "ERROR: 프레임 로드 실패"),
}


def load_json(path: Path) -> dict | None:
    """JSON 파일을 로드한다."""
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def process_single_video(video_stem: str, analysis_base: Path, rules_version: int) -> None:
    """단일 영상의 자동 판정을 수행한다."""
    analysis_dir = analysis_base / video_stem

    # 사전 분석 결과 로드
    prefilter = load_json(analysis_dir / "prefilter.json")
    visual_pf = load_json(analysis_dir / "visual_prefilter.json")

    if prefilter is None:
        print(f"  prefilter.json 없음. Pass 1을 먼저 실행하세요.")
        return
    if visual_pf is None:
        print(f"  visual_prefilter.json 없음. Pass 1.5를 먼저 실행하세요.")
        return

    # 인덱싱
    text_map = {s["scene_id"]: s for s in prefilter["scenes"]}
    visual_map = {s["scene_id"]: s for s in visual_pf["scenes"]}

    # 장면 파일 순회 + 판정
    scene_files = sorted(analysis_dir.glob("scene_*.json"))
    stats = {"important": 0, "not_important": 0, "already_judged": 0}

    for sf in scene_files:
        with open(sf, encoding="utf-8") as f:
            scene = json.load(f)

        sid = scene["scene_id"]

        # 이미 현재 버전으로 판정된 장면은 스킵
        if scene.get("importance_rule_version", 0) >= rules_version:
            stats["already_judged"] += 1
            continue

        text_hint = text_map.get(sid, {}).get("prefilter_hint", "NEEDS_VISUAL_CHECK")
        visual_class = visual_map.get(sid, {}).get("visual_class", "ERROR")

        key = (visual_class, text_hint)
        is_important, reason = DECISION_MATRIX.get(key, (False, f"UNKNOWN: {key}"))

        # 판정 결과 기록
        scene["is_important_frame"] = is_important
        scene["importance_reason"] = reason
        scene["importance_rule_version"] = rules_version

        with open(sf, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=2)

        if is_important:
            stats["important"] += 1
        else:
            stats["not_important"] += 1

    total = stats["important"] + stats["not_important"]
    print(f"  자동 판정 완료: {total}개 판정")
    print(f"    중요 프레임: {stats['important']}개")
    print(f"    비중요 프레임: {stats['not_important']}개")
    if stats["already_judged"]:
        print(f"    이미 판정됨 (스킵): {stats['already_judged']}개")


def main():
    """Stage 3C-3: 자동 중요도 판정."""
    config = load_config()
    analysis_base = get_path(config, "workspace_analysis")

    # 규칙 버전 로드
    rules_path = Path(__file__).parent / "importance_rules.json"
    if not rules_path.exists():
        print("오류: importance_rules.json이 없습니다.")
        sys.exit(1)

    with open(rules_path, encoding="utf-8") as f:
        rules = json.load(f)
    rules_version = rules["version"]

    video_dirs = sorted(
        d for d in analysis_base.iterdir()
        if d.is_dir() and list(d.glob("scene_*.json"))
    )
    if not video_dirs:
        print("오류: 장면 분석 파일이 없습니다.")
        sys.exit(1)

    print(f"\n=== Stage 3C-3: 자동 중요도 판정 ===")
    print(f"규칙 버전: {rules_version}")
    print(f"영상 {len(video_dirs)}개 처리:")

    for vdir in video_dirs:
        stem = vdir.name
        print(f"\n--- [{stem}] ---")
        process_single_video(stem, analysis_base, rules_version)

    print(f"\n=== Stage 3C-3 전체 완료 ===")
    print(f"\n다음 단계: 08_generate_report.py로 HWPX 보고서를 재생성하세요.")
    print(f"  기존 .hwpx 파일을 삭제한 후 실행하면 됩니다.")


if __name__ == "__main__":
    main()
