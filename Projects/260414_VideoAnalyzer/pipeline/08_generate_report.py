"""
VideoAnalyzer Pipeline - Stage 5: HWPX 보고서 생성
통합 분석 결과 + 레퍼런스 + 원본 프레임 이미지를 HWPX에 삽입하여
한/글 호환 AI 분석 보고서를 생성한다.
이미지 아래에 AI용 텍스트 설명서(이미지 디스크립터)를 배치한다.

v4: 2-Phase 이미지 삽입 (python-hwpx 텍스트 -> 한/글 COM 이미지)
  python-hwpx 단독 이미지 삽입은 한/글 호환성 문제로 사용 불가.
  Phase 1: python-hwpx로 텍스트 전용 HWPX + 이미지 위치 마커
  Phase 2: 한/글 COM (HWPFrame.HwpObject)으로 마커를 실제 이미지로 교체
"""
import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import hwpx
from PIL import Image

from config_loader import load_config
from path_utils import get_path, ensure_dir

# HWPX 스타일 ID 상수
STYLE_BODY = 1      # 본문
STYLE_H1 = 2        # 개요 1
STYLE_H2 = 3        # 개요 2
STYLE_H3 = 4        # 개요 3
STYLE_CAPTION = 22  # 캡션

# 이미지 마커 패턴 -- COM 후처리에서 실제 이미지로 교체
_IMG_MARKER_FMT = "<<IMG:{name}>>"

# A4 본문 폭 (mm) -- COM 이미지 크기 제한용
# 한/글 기본 여백 좌우 30mm -> 210-60=150mm. horzsize=42520 HWPU 확인.
_BODY_WIDTH_MM = 150
_HWPU_PER_MM = 283.465


def resize_image_to_file(src: Path, max_width: int, quality: int,
                         dest_dir: Path):
    """이미지를 리사이즈하고 본문 폭에 맞는 DPI로 JPEG 저장한다.

    DPI를 계산하여 한/글 InsertPicture가 본문 폭(160mm)에 맞게 표시하도록 한다.

    Returns:
        (temp_path, width_px, height_px) 또는 None
    """
    if not src.exists():
        return None
    img = Image.open(src)
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    out = dest_dir / f"{src.stem}.jpg"
    # DPI 설정: 이미지가 본문 폭(160mm)에 맞도록 계산
    target_dpi = max(72, int(img.width / (_BODY_WIDTH_MM / 25.4)))
    img.convert("RGB").save(out, format="JPEG", quality=quality,
                            dpi=(target_dpi, target_dpi))
    return out, img.width, img.height


# -- 텍스트 헬퍼 ----------------------------------------------------------

def add_heading(doc: hwpx.HwpxDocument, text: str, level: int = 1) -> None:
    """제목 단락을 추가한다."""
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


def write_image_descriptor(doc: hwpx.HwpxDocument, scene: dict) -> None:
    """AI용 이미지 설명서를 HWPX 단락으로 추가한다."""
    mins = int(scene["start_time"] // 60)
    secs = int(scene["start_time"] % 60)

    va = scene.get("visual_analysis", {})
    ia = scene.get("integrated_analysis", {})

    add_caption(doc, f"[AI 이미지 분석서] {scene['frame_name']} -- {mins}:{secs:02d}")
    add_caption(doc, f"  화면 구성: {va.get('layout', '(분석 필요)')}")
    add_caption(doc, f"  시각 핵심 정보: {ia.get('visual_only_info', '(분석 필요)')}")

    for label, key in [("수식 재현", "extracted_formulas"),
                       ("코드 재현", "extracted_code"),
                       ("구조 재현", "extracted_diagrams")]:
        items = va.get(key, [])
        if items:
            add_caption(doc, f"  {label}:")
            for item in items:
                add_caption(doc, f"    {item}")

    add_caption(doc, f"  학습 포인트: {ia.get('combined_insight', '(분석 필요)')}")
    add_empty_line(doc)


# -- Phase 2: 한/글 COM 이미지 삽입 ----------------------------------------

def _replace_markers_with_images(hwpx_path: Path,
                                 image_entries: list[tuple]) -> int:
    """한/글 COM 자동화로 HWPX 내 텍스트 마커를 실제 이미지로 교체한다.

    HWPX_Master 스킬의 insert_image_ole.py 패턴 적용.
    python-hwpx 단독 이미지 삽입이 한/글과 호환되지 않아 COM으로 전환.

    Args:
        hwpx_path: HWPX 파일 절대경로
        image_entries: [(frame_name, img_abs_path, w_px, h_px), ...]

    Returns:
        삽입된 이미지 수
    """
    import win32com.client as win32

    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FileCheck")
    hwp.XHwpWindows.Item(0).Visible = False

    try:
        hwp.Open(str(hwpx_path))

        inserted = 0
        for frame_name, img_path, w_px, h_px in image_entries:
            marker = _IMG_MARKER_FMT.format(name=frame_name)

            # 문서 처음으로 이동
            hwp.MovePos(2)  # moveBOF

            # 마커 찾기
            pset = hwp.HParameterSet.HFindReplace
            hwp.HAction.GetDefault("RepeatFind", pset.HSet)
            pset.FindString = marker
            pset.Direction = 0   # Forward
            pset.IgnoreMessage = 1

            if not hwp.HAction.Execute("RepeatFind", pset.HSet):
                print(f"    마커 못찾음: {frame_name}")
                continue

            # 찾은 마커 선택 후 삭제
            hwp.HAction.Run("Cancel")
            for _ in range(len(marker)):
                hwp.HAction.Run("MoveLeft")
            for _ in range(len(marker)):
                hwp.HAction.Run("MoveSelRight")
            hwp.HAction.Run("Delete")

            # 이미지 삽입 (sizeoption=2: 문단에 맞춤 -- 본문 폭 자동 맞춤)
            ctrl = hwp.InsertPicture(
                str(img_path), True, 2, False, False, 0,
            )
            if ctrl is not None:
                inserted += 1

        hwp.SaveAs(str(hwpx_path), "HWPX")
    finally:
        try:
            hwp.Quit()
        except Exception:
            pass

    return inserted


# -- 보고서 생성 -----------------------------------------------------------

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
    """HWPX 보고서를 생성한다.

    Phase 1: python-hwpx로 텍스트 + 이미지 마커 HWPX 저장
    Phase 2: 한/글 COM으로 마커를 실제 이미지로 교체
    """
    video_name = manifest.get("video_name", "unknown")
    total_scenes = manifest.get("total_scenes", 0)
    duration = manifest.get("total_duration", 0)

    doc = hwpx.HwpxDocument.new()

    # -- 헤더 --
    add_heading(doc, f"AI 분석 보고서: {video_name}", level=1)
    add_empty_line(doc)
    add_body(doc, f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    add_body(doc, f"영상 길이: {duration:.1f}초 ({duration/60:.1f}분)")
    add_body(doc, f"분석 장면: {total_scenes}개")
    add_body(doc, f"자막 출처: {manifest.get('transcript_source', 'unknown')}")
    add_empty_line(doc)

    # -- 장면별 섹션 --
    image_frames = []  # [(frame_name, frame_path), ...]
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

        # 중요 프레임: 마커 삽입 + AI 설명서
        va = scene.get("visual_analysis", {})
        has_analysis = bool(va.get("layout", ""))
        if scene.get("is_important_frame", False) and has_analysis:
            frame_path = frames_dir / scene["frame_name"]
            if frame_path.exists():
                add_body(doc, _IMG_MARKER_FMT.format(name=scene["frame_name"]))
                image_frames.append((scene["frame_name"], frame_path))
                write_image_descriptor(doc, scene)

        # 통합 분석
        ia = scene.get("integrated_analysis", {})
        if ia.get("combined_insight"):
            add_heading(doc, "통합 분석", level=3)
            add_body(doc, ia["combined_insight"])

        if ia.get("visual_only_info"):
            add_body(doc, f"시각 전용 정보: {ia['visual_only_info']}")

        add_empty_line(doc)

    # -- 레퍼런스 섹션 --
    if references:
        add_heading(doc, "레퍼런스 자료", level=2)
        for i, ref in enumerate(references, 1):
            add_heading(doc, f"레퍼런스 {i}: {ref.get('keyword', '')}", level=3)
            add_body(doc, f"출처: {ref.get('url', 'N/A')}")
            add_body(doc, f"검증 결과: {ref.get('verification', 'N/A')}")
            if ref.get("content"):
                add_body(doc, f"내용 요약: {ref['content'][:500]}")
            add_empty_line(doc)

    # -- Phase 1: 텍스트 전용 HWPX 저장 --
    ensure_dir(output_path.parent)
    doc.save_to_path(str(output_path))
    print(f"  Phase 1 완료: 텍스트 HWPX 저장 ({len(image_frames)}개 이미지 마커)")

    # -- Phase 2: 한/글 COM 이미지 삽입 --
    # HWP InsertPicture는 내부 96 DPI 기준 픽셀 크기로만 표시한다.
    # 본문 폭(160mm)에 맞추려면 160/25.4*96 = 605px로 리사이즈 필요.
    hwp_body_px = int(_BODY_WIDTH_MM / 25.4 * 96)
    image_count = 0
    if image_frames:
        temp_dir = Path(tempfile.mkdtemp(prefix="va_img_"))
        try:
            entries = []
            for frame_name, frame_path in image_frames:
                result = resize_image_to_file(
                    frame_path, hwp_body_px, quality, temp_dir,
                )
                if result:
                    tmp_path, w, h = result
                    entries.append((frame_name, tmp_path.resolve(), w, h))

            if entries:
                print(f"  Phase 2 시작: COM 이미지 삽입 ({len(entries)}장)...")
                image_count = _replace_markers_with_images(
                    output_path.resolve(), entries,
                )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"보고서 생성 완료: {output_path}")
    print(f"  장면: {total_scenes}개, 삽입 이미지: {image_count}장")


def process_single_video(video_stem: str, manifest_base: Path,
                         analysis_base: Path, research_base: Path,
                         frames_base: Path, output_dir: Path,
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
