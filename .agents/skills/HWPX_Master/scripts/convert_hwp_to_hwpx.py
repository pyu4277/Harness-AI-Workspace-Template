"""
HWP -> HWPX 자동 변환 (Convert-and-Archive 패턴)
=================================================

목적:
  HWPX_Master 스킬이 .hwp 입력을 받았을 때 자동으로 .hwpx로 변환하여
  Track A/B/C/D가 동일한 XML 기반 처리 흐름을 재사용할 수 있게 한다.

처리 순서:
  1. OLE2 시그니처 검증 (d0cf11e0a1b11ae1)
  2. pywin32 COM (HWPFrame.HwpObject) 로 한컴 오피스 엔진 호출
  3. RegisterModule("FilePathCheckDLL", "AutomationModule") 보안 모듈 등록
  4. Open(src, "HWP", "forceopen:true")
  5. SaveAs(dst, "HWPX", "") -- 한컴 엔진이 OLE2 -> OPC XML 무손실 재작성
  6. 출력 HWPX 검증 (ZIP 시그니처 + mimetype + section0 구조 카운트)
  7. 검증 성공 시 원본 .hwp -> .hwp-archive/ 이동 (영구 삭제 금지)
  8. 검증 실패 시 .hwpx 삭제 + 원본 유지 + 오류 반환

Convert-and-Archive 안전 원칙:
  - 영구 삭제 금지: 원본은 .hwp-archive/YYMMDD-HHMMSS_원본명.hwp 로 이동
  - 사용자 의도 달성: 원본 폴더에서 .hwp 사라지고 .hwpx 가 그 자리에 생김
  - 복구 가능: 사용자가 직접 .hwp-archive/ 폴더를 확인하거나 비울 수 있음

사용법 (CLI):
  python convert_hwp_to_hwpx.py <hwp-path>

  성공 시 stdout 에 변환된 .hwpx 절대경로 출력 (다음 스크립트가 파싱 가능)
  실패 시 exit code 1 + stderr 에 오류 메시지
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
import zipfile

try:
    import olefile
except ImportError:
    sys.stderr.write("[convert_hwp_to_hwpx] ERROR: olefile not installed. Run: pip install olefile\n")
    sys.exit(2)


OLE2_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
HWPX_MIMETYPE = "application/hwp+zip"
ARCHIVE_SUBDIR = ".hwp-archive"


def log(msg: str) -> None:
    sys.stderr.write(f"[convert_hwp_to_hwpx] {msg}\n")


def is_valid_hwp_binary(path: str) -> tuple[bool, str]:
    """HWP OLE2 Compound Document 여부 검증."""
    if not os.path.exists(path):
        return False, f"파일 없음: {path}"
    if not os.path.isfile(path):
        return False, f"파일이 아님: {path}"
    with open(path, "rb") as f:
        sig = f.read(8)
    if sig != OLE2_SIGNATURE:
        return False, f"OLE2 시그니처 불일치: {sig.hex()}"
    if not olefile.isOleFile(path):
        return False, "olefile.isOleFile() False"
    try:
        ole = olefile.OleFileIO(path)
        streams = [s for s in ole.listdir()]
        ole.close()
    except Exception as exc:
        return False, f"OLE 파싱 실패: {exc}"
    has_fileheader = any("FileHeader" in "/".join(s) for s in streams)
    if not has_fileheader:
        return False, "FileHeader 스트림 없음 (HWP 아님)"
    return True, "OK"


def verify_hwpx_output(path: str) -> tuple[bool, dict]:
    """출력 .hwpx 가 유효한 OPC ZIP 구조인지 검증."""
    details: dict = {}
    if not os.path.exists(path):
        return False, {"error": "파일 생성 실패"}
    details["size"] = os.path.getsize(path)
    with open(path, "rb") as f:
        sig = f.read(4)
    details["zip_signature"] = sig.hex()
    if sig != b"PK\x03\x04":
        return False, details
    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            details["entry_count"] = len(names)
            if "mimetype" not in names:
                details["error"] = "mimetype 엔트리 없음"
                return False, details
            mimetype = zf.read("mimetype").decode("utf-8", errors="replace").strip()
            details["mimetype"] = mimetype
            if mimetype != HWPX_MIMETYPE:
                details["error"] = f"mimetype 불일치 ({mimetype})"
                return False, details
            section0 = next((n for n in names if "section0.xml" in n), None)
            if not section0:
                details["error"] = "Contents/section0.xml 없음"
                return False, details
            s0_data = zf.read(section0).decode("utf-8", errors="replace")
            details["paragraphs"] = s0_data.count("<hp:p ")
            details["tables"] = s0_data.count("<hp:tbl ")
            details["runs"] = s0_data.count("<hp:run")
            details["text_nodes"] = s0_data.count("<hp:t>")
    except zipfile.BadZipFile as exc:
        details["error"] = f"BadZipFile: {exc}"
        return False, details
    return True, details


def archive_original_hwp(src_hwp: str) -> str:
    """원본 .hwp 를 .hwp-archive/YYMMDD-HHMMSS_원본명.hwp 로 이동.

    Returns: 아카이브 경로
    Raises: OSError on move failure
    """
    src_dir = os.path.dirname(os.path.abspath(src_hwp))
    archive_dir = os.path.join(src_dir, ARCHIVE_SUBDIR)
    os.makedirs(archive_dir, exist_ok=True)
    ts = _dt.datetime.now().strftime("%y%m%d-%H%M%S")
    basename = os.path.basename(src_hwp)
    archive_name = f"{ts}_{basename}"
    archive_path = os.path.join(archive_dir, archive_name)
    # 충돌 방지
    counter = 1
    while os.path.exists(archive_path):
        archive_name = f"{ts}_{counter}_{basename}"
        archive_path = os.path.join(archive_dir, archive_name)
        counter += 1
    os.replace(src_hwp, archive_path)
    return archive_path


def convert_via_pywin32(src_hwp: str, dst_hwpx: str) -> bool:
    """pywin32 COM 을 통한 한컴 오피스 SaveAs HWPX 변환.

    Returns: True on success, raises on fatal error.
    """
    try:
        import win32com.client
        import pythoncom
    except ImportError as exc:
        raise RuntimeError(f"pywin32 not installed: {exc}")

    pythoncom.CoInitialize()
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "AutomationModule")
        open_ok = hwp.Open(os.path.abspath(src_hwp), "HWP", "forceopen:true")
        if not open_ok:
            raise RuntimeError(f"HWP Open 실패: {src_hwp}")
        save_ok = hwp.SaveAs(os.path.abspath(dst_hwpx), "HWPX", "")
        if not save_ok:
            raise RuntimeError(f"HWPX SaveAs 실패: {dst_hwpx}")
        try:
            hwp.Quit()
        except Exception as quit_exc:
            # Quit 오류는 무해 (com_error -2147023179 등). 파일 저장은 이미 완료.
            log(f"Quit() 경고 (무시): {quit_exc}")
        return True
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def convert_hwp_to_hwpx(src_hwp: str) -> dict:
    """HWP -> HWPX 변환 엔드투엔드.

    Returns:
      dict with keys:
        status: "success" | "failed"
        hwpx_path: 변환된 .hwpx 절대경로 (성공 시)
        archive_path: 아카이브된 원본 .hwp 절대경로 (성공 시)
        stats: verify_hwpx_output details
        error: 오류 메시지 (실패 시)
    """
    src_abs = os.path.abspath(src_hwp)

    # 1. 입력 검증
    valid, reason = is_valid_hwp_binary(src_abs)
    if not valid:
        return {"status": "failed", "error": f"입력 검증 실패: {reason}"}
    log(f"입력 검증 OK: {src_abs}")
    log(f"원본 크기: {os.path.getsize(src_abs)} bytes")

    # 2. 출력 경로 결정 (같은 폴더, 확장자만 .hwpx)
    src_dir = os.path.dirname(src_abs)
    src_stem = os.path.splitext(os.path.basename(src_abs))[0]
    dst_hwpx = os.path.join(src_dir, src_stem + ".hwpx")

    # 출력 파일 이미 존재 시 충돌 방지
    if os.path.exists(dst_hwpx):
        ts = _dt.datetime.now().strftime("%y%m%d-%H%M%S")
        dst_hwpx = os.path.join(src_dir, f"{src_stem}_{ts}.hwpx")
        log(f"기존 .hwpx 충돌 회피: {dst_hwpx}")

    # 3. 변환 실행
    try:
        convert_via_pywin32(src_abs, dst_hwpx)
    except Exception as exc:
        # 실패 시 부분 출력 파일 삭제
        if os.path.exists(dst_hwpx):
            try:
                os.remove(dst_hwpx)
            except OSError:
                pass
        return {"status": "failed", "error": f"변환 실패: {exc}"}
    log(f"변환 완료: {dst_hwpx}")

    # 4. 출력 검증
    ok, stats = verify_hwpx_output(dst_hwpx)
    if not ok:
        # 검증 실패 시 출력 삭제 + 원본 유지
        try:
            os.remove(dst_hwpx)
        except OSError:
            pass
        return {
            "status": "failed",
            "error": f"출력 HWPX 검증 실패: {stats}",
        }
    log(
        f"검증 OK: {stats['size']} bytes, "
        f"문단={stats['paragraphs']}, 표={stats['tables']}, "
        f"런={stats['runs']}, 텍스트 노드={stats['text_nodes']}"
    )

    # 5. 원본 아카이브 이동
    try:
        archive_path = archive_original_hwp(src_abs)
    except OSError as exc:
        return {
            "status": "failed",
            "error": f"원본 아카이브 이동 실패: {exc}",
            "hwpx_path": dst_hwpx,
        }
    log(f"원본 아카이브: {archive_path}")

    return {
        "status": "success",
        "hwpx_path": dst_hwpx,
        "archive_path": archive_path,
        "stats": stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="HWP -> HWPX 자동 변환 (Convert-and-Archive)"
    )
    parser.add_argument("hwp_path", help="입력 .hwp 파일 경로 (절대/상대)")
    parser.add_argument(
        "--json",
        action="store_true",
        help="결과를 JSON 으로 stdout 에 출력",
    )
    args = parser.parse_args()

    result = convert_hwp_to_hwpx(args.hwp_path)

    if args.json:
        import json

        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
    else:
        if result["status"] == "success":
            sys.stdout.write(result["hwpx_path"] + "\n")
        else:
            sys.stderr.write(f"ERROR: {result.get('error', 'unknown')}\n")

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
