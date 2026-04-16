"""
VideoAnalyzer Pipeline - Stage 3B: 통합 분석
시각 분석 + 텍스트 분석 결과를 통합하고 레퍼런스 니즈를 감지한다.
실제 분석은 Claude Code 런타임에서 LLM이 수행한다.
"""
import json
import sys
from pathlib import Path

from config_loader import load_config
from path_utils import get_path, ensure_dir


def create_analysis_template(scene: dict) -> dict:
    """장면별 분석 결과 템플릿을 생성한다."""
    return {
        "scene_id": scene["scene_id"],
        "frame_name": scene.get("representative_frame", ""),
        "start_time": scene["start_time"],
        "end_time": scene["end_time"],
        "visual_analysis": {
            "layout": "",
            "elements": [],
            "extracted_formulas": [],
            "extracted_code": [],
            "extracted_diagrams": [],
        },
        "text_analysis": {
            "key_concepts": [],
            "summary": scene.get("transcript_text", ""),
        },
        "integrated_analysis": {
            "visual_only_info": "",
            "text_only_info": "",
            "combined_insight": "",
        },
        "reference_needs": [],
        "is_important_frame": False,
    }


def main():
    """Stage 3B: 통합 분석 템플릿 생성."""
    config = load_config()

    manifest_dir = get_path(config, "workspace_manifest")
    analysis_dir = get_path(config, "workspace_analysis")
    ensure_dir(analysis_dir)

    manifest_path = manifest_dir / "manifest.json"
    if not manifest_path.exists():
        print("오류: manifest.json이 없습니다. Stage 2를 먼저 실행하세요.")
        sys.exit(1)

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    scenes = manifest["scenes"]
    print(f"\n=== Stage 3B: 통합 분석 템플릿 생성 ===")

    templates_created = 0
    for scene in scenes:
        scene_file = analysis_dir / f"scene_{scene['scene_id']:03d}.json"
        if scene_file.exists():
            print(f"  [{scene['scene_id']:3d}] 이미 존재, 건너뜀")
            continue

        template = create_analysis_template(scene)
        with open(scene_file, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        templates_created += 1

    print(f"템플릿 생성: {templates_created}개 -> {analysis_dir}")
    print()
    print("=" * 60)
    print("다음 단계: Claude Code에서 각 장면을 통합 분석하세요.")
    print("  1. 프레임 이미지 Read (시각 분석) -- 텍스트만 분석 금지!")
    print("  2. 자막 텍스트 분석 (텍스트 분석)")
    print("  3. 시각+텍스트 통합 (자막에 없는 시각 정보 보완)")
    print("  4. 레퍼런스 필요 여부 판단 (reference_needs에 키워드 추가)")
    print("  5. 중요 프레임 판단 (is_important_frame = true)")
    print("  6. scene_NNN.json 갱신")
    print("=" * 60)


if __name__ == "__main__":
    main()
