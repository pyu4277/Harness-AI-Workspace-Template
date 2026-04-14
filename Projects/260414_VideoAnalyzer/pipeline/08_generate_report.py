"""
VideoAnalyzer Pipeline - Stage 5: HWPX 보고서 생성
통합 분석 결과 + 레퍼런스 + 원본 프레임 이미지를 HWPX에 삽입하여
한/글 호환 AI 분석 보고서를 생성한다.
이미지 아래에 AI용 텍스트 설명서(이미지 디스크립터)를 배치한다.

개량 v3: Markdown -> HWPX 출력 전환 (python-hwpx v2.8)
"""
import io
import json
import sys
from datetime import datetime
from pathlib import Path

import hwpx
from PIL import Image

from config_loader import load_config
from path_utils import get_path, ensure_dir

# HWPX 스타일 ID 상수
STYLE_NORMAL = 0    # 바탕글
STYLE_BODY = 1      # 본문
STYLE_H1 = 2        # 개요 1
STYLE_H2 = 3        # 개요 2
STYLE_H3 = 4        # 개요 3
STYLE_CAPTION = 22  # 캡션

# HWPX 단위: 7200 units = 1 inch. 96dpi 기준 pixel * 75 = hwpunit
HWPUNIT_PER_PIXEL = 75
# A4 여백 제외 본문 폭 약 160mm = 6.3in = 45360 units
MAX_BODY_WIDTH_HWPUNIT = 45360


def resize_image_bytes(image_path: Path, max_width: int, quality: int) -> tuple[bytes, int, int]:
    """이미지를 리사이즈하고 JPEG 바이트로 반환한다. (bytes, width_px, height_px)"""
    img = Image.open(image_path)
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality)
    return buf.getvalue(), img.width, img.height


def pixel_to_hwpunit(px: int) -> int:
    """픽셀을 HWPX 단위로 변환한다."""
    return px * HWPUNIT_PER_PIXEL


def add_heading(doc: hwpx.HwpxDocument, text: str, level: int = 1) -> None:
    """제목 단락을 추가한다. level: 1=H1, 2=H2, 3=H3"""
    style_map = {1: STYLE_H1, 2: STYLE_H2, 3: STYLE_H3}
    doc.add_paragraph(text, style_id_ref=style_map.get(level, STYLE_H1))


def add_body(doc: hwpx.HwpxDocument, text: str) -> None:
    """본문 단락을 추가한다."""
    doc.add_paragraph(text, style_id_ref=STYLE_BODY)


def add_caption(doc: hwpx.HwpxDocument, text: str) -> None:
    """캡션 스타일 단락을 추가한다."""
    doc.add_paragraph(text, style_id_ref=STYLE_CAPTION)


def add_empty_line(doc: hwpx.HwpxDocument) -> None:
    """빈 줄을 추가한다."""
    doc.add_paragraph("", style_id_ref=STYLE_BODY)


def insert_frame_image(doc: hwpx.HwpxDocument, image_path: Path,
                       max_width: int, quality: int) -> bool:
    """프레임 이미지를 문서에 삽입한다. 성공 여부를 반환한다."""
    if not image_path.exists():
        return False

    img_bytes, w_px, h_px = resize_image_bytes(image_path, max_width, quality)

    # 픽셀 -> HWPX 단위 변환, 본문 폭 초과 방지
    w_hwp = min(pixel_to_hwpunit(w_px), MAX_BODY_WIDTH_HWPUNIT)
    scale = w_hwp / pixel_to_hwpunit(w_px)
    h_hwp = int(pixel_to_hwpunit(h_px) * scale)

    item_id = doc.add_image(img_bytes, "jpg")
    doc.add_shape("pic", attributes={
        "binaryItemIDRef": item_id,
        "width": str(w_hwp),
        "height": str(h_hwp),
    })
    return True


def write_image_descriptor(doc: hwpx.HwpxDocument, scene: dict) -> None:
    """AI용 이미지 설명서를 HWPX 단락으로 추가한다."""
    mins = int(scene["start_time"] // 60)
    secs = int(scene["start_time"] % 60)

    va = scene.get("visual_analysis", {})
    ia = scene.get("integrated_analysis", {})

    add_caption(doc, f"[AI 이미지 분석서] {scene['frame_name']} -- {mins}:{secs:02d}")
    add_caption(doc, f"  화면 구성: {va.get('layout', '(분석 필요)')}")
    add_caption(doc, f"  시각 핵심 정보: {ia.get('visual_only_info', '(분석 필요)')}")

    # 수식 재현
    formulas = va.get("extracted_formulas", [])
    if formulas:
        add_caption(doc, "  수식 재현:")
        for formula in formulas:
            add_caption(doc, f"    {formula}")

    # 코드 재현
    codes = va.get("extracted_code", [])
    if codes:
        add_caption(doc, "  코드 재현:")
        for code in codes:
            add_caption(doc, f"    {code}")

    # 다이어그램 재현
    diagrams = va.get("extracted_diagrams", [])
    if diagrams:
        add_caption(doc, "  구조 재현:")
        for diagram in diagrams:
            add_caption(doc, f"    {diagram}")

    add_caption(doc, f"  학습 포인트: {ia.get('combined_insight', '(분석 필요)')}")
    add_empty_line(doc)


def load_references(research_dir: Path) -> list[dict]:
    """수집된 레퍼런스를 로드한다."""
    refs = []
    for ref_file in sorted(research_dir.glob("ref_*.json")):
        with open(ref_file, encoding="utf-8") as f:
            refs.append(json.load(f))
    return refs


def generate_report(
    manifest: dict,
    scenes_analysis: list[dict],
    references: list[dict],
    frames_dir: Path,
    output_path: Path,
    max_width: int,
    quality: int,
) -> None:
    """HWPX 최종 보고서를 생성한다."""
    video_name = manifest.get("video_name", "unknown")
    total_scenes = manifest.get("total_scenes", 0)
    duration = manifest.get("total_duration", 0)

    doc = hwpx.HwpxDocument.new()

    # --- 헤더 ---
    add_heading(doc, f"AI 분석 보고서: {video_name}", level=1)
    add_empty_line(doc)
    add_body(doc, f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    add_body(doc, f"영상 길이: {duration:.1f}초 ({duration/60:.1f}분)")
    add_body(doc, f"분석 장면: {total_scenes}개")
    add_body(doc, f"자막 출처: {manifest.get('transcript_source', 'unknown')}")
    add_empty_line(doc)

    # --- 장면별 섹션 ---
    image_count = 0
    for scene in scenes_analysis:
        sid = scene["scene_id"]
        mins = int(scene["start_time"] // 60)
        secs = int(scene["start_time"] % 60)

        add_heading(doc, f"장면 {sid} ({mins}:{secs:02d})", level=2)
        add_body(doc, f"시간: {mins}:{secs:02d} ~ {scene['end_time']:.1f}초")

        # 자막 텍스트
        ta = scene.get("text_analysis", {})
        transcript = ta.get("summary", "")
        if transcript:
            add_heading(doc, "자막 내용", level=3)
            add_body(doc, transcript)

        # 핵심 개념
        concepts = ta.get("key_concepts", [])
        if concepts:
            add_body(doc, f"핵심 개념: {', '.join(concepts)}")

        # 중요 프레임: 이미지 삽입 + AI 설명서
        # visual_analysis.layout이 채워진 프레임만 삽입 (분석 미완료 프레임 제외)
        va = scene.get("visual_analysis", {})
        has_analysis = bool(va.get("layout", ""))
        if scene.get("is_important_frame", False) and has_analysis:
            frame_path = frames_dir / scene["frame_name"]
            if insert_frame_image(doc, frame_path, max_width, quality):
                image_count += 1
                write_image_descriptor(doc, scene)

        # 통합 분석
        ia = scene.get("integrated_analysis", {})
        if ia.get("combined_insight"):
            add_heading(doc, "통합 분석", level=3)
            add_body(doc, ia["combined_insight"])

        if ia.get("visual_only_info"):
            add_body(doc, f"시각 전용 정보: {ia['visual_only_info']}")

        add_empty_line(doc)

    # --- 레퍼런스 섹션 ---
    if references:
        add_heading(doc, "레퍼런스 자료", level=2)
        for i, ref in enumerate(references, 1):
            add_heading(doc, f"레퍼런스 {i}: {ref.get('keyword', '')}", level=3)
            add_body(doc, f"출처: {ref.get('url', 'N/A')}")
            add_body(doc, f"검증 결과: {ref.get('verification', 'N/A')}")
            if ref.get("content"):
                add_body(doc, f"내용 요약: {ref['content'][:500]}")
            add_empty_line(doc)

    # --- 저장 ---
    ensure_dir(output_path.parent)
    doc.save_to_path(str(output_path))

    print(f"보고서 생성 완료: {output_path}")
    print(f"  장면: {total_scenes}개")
    print(f"  삽입 이미지: {image_count}장")


def process_single_video(video_stem: str, manifest_base: Path, analysis_base: Path,
                          research_base: Path, frames_base: Path, output_dir: Path,
                          max_width: int, quality: int) -> None:
    """단일 영상의 HWPX 보고서를 생성한다."""
    manifest_dir = manifest_base / video_stem
    analysis_dir = analysis_base / video_stem
    research_dir = research_base / video_stem
    frames_dir = frames_base / video_stem

    manifest_path = manifest_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"  manifest.json 없음. Stage 2B를 먼저 실행하세요.")
        return

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    # 분석 결과 로드
    scenes_analysis = []
    if analysis_dir.exists():
        for scene_file in sorted(analysis_dir.glob("scene_*.json")):
            with open(scene_file, encoding="utf-8") as f:
                scenes_analysis.append(json.load(f))

    if not scenes_analysis:
        print(f"  분석 결과 없음. Stage 3을 먼저 실행하세요.")
        return

    # 레퍼런스 로드
    references = load_references(research_dir) if research_dir.exists() else []

    # 출력 파일명: .hwpx 확장자
    date_str = datetime.now().strftime("%y%m%d")
    output_path = output_dir / f"{date_str}_{video_stem}_AI분석보고서.hwpx"

    if output_path.exists():
        print(f"  보고서 이미 존재. 건너뜁니다.")
        return

    generate_report(
        manifest, scenes_analysis, references,
        frames_dir, output_path,
        max_width, quality,
    )


def main():
    """Stage 5: 모든 영상의 HWPX 보고서 생성."""
    config = load_config()

    manifest_base = get_path(config, "workspace_manifest")
    analysis_base = get_path(config, "workspace_analysis")
    research_base = get_path(config, "workspace_research")
    frames_base = get_path(config, "workspace_frames")
    output_dir = get_path(config, "output")
    ensure_dir(output_dir)

    max_width = config["report"]["image_max_width"]
    quality = config["report"]["image_quality"]

    # manifest.json이 존재하는 영상 서브디렉토리 탐색
    video_dirs = sorted(
        d for d in manifest_base.iterdir()
        if d.is_dir() and (d / "manifest.json").exists()
    )
    if not video_dirs:
        print("오류: manifest.json이 없습니다. Stage 2를 먼저 실행하세요.")
        sys.exit(1)

    print(f"\n=== Stage 5: HWPX 보고서 생성 ===")
    print(f"영상 {len(video_dirs)}개 처리:")

    for vdir in video_dirs:
        stem = vdir.name
        print(f"\n--- [{stem}] ---")
        process_single_video(
            stem, manifest_base, analysis_base, research_base,
            frames_base, output_dir, max_width, quality,
        )

    print(f"\n=== Stage 5 전체 완료 ===")


if __name__ == "__main__":
    main()
