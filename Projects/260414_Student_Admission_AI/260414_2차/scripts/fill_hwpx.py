"""HWPX 자소서 양식 채우기 -- 양식 보존 출력 파이프라인.

사용자 결정 (2026-04-14): 출력은 입력 양식 확장자 echo. HWPX -> HWPX.
원본 HWPX 의 Contents/section0.xml 헤더 paragraph 다음의 빈 paragraph 에 답변 텍스트 삽입.
헤더 자수 카운터 (`0/400` -> `actual/400`) 도 갱신.

입력: --form (원본 HWPX) --answers (JSON: {"q1": "...", "q2": "...", ...}) --output (결과 HWPX)
종료 코드: 0=성공, 1=자수 초과, 2=양식 파싱 실패
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

QUESTION_PATTERN = re.compile(
    r"<hp:t>(\d+)\.\s*([^<0-9]+?)\s*0/(\d+)</hp:t>"
)


def count_chars(text: str) -> int:
    """공백 포함 문자 수 (한글 양식 표준)."""
    return len(text.replace("\r\n", "\n"))


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def fill_section_xml(xml: str, answers: dict[str, str]) -> str:
    """헤더의 자수 카운터 갱신 + 다음 빈 paragraph 에 답변 텍스트 삽입."""
    questions = list(QUESTION_PATTERN.finditer(xml))
    if not questions:
        print("[ERR] 양식에서 질문 헤더를 찾지 못함", file=sys.stderr)
        sys.exit(2)

    if len(questions) != len(answers):
        print(
            f"[WARN] 질문 수({len(questions)}) != 답변 수({len(answers)})",
            file=sys.stderr,
        )

    # 끝에서 앞으로 처리해야 인덱스가 안 밀린다
    for q in reversed(questions):
        qnum = q.group(1)
        qtitle = q.group(2).strip()
        qlimit = int(q.group(3))
        akey = f"q{qnum}"
        if akey not in answers:
            continue
        atext = answers[akey].strip()
        actual = count_chars(atext)
        if actual > qlimit:
            print(
                f"[ERR] Q{qnum} ({qtitle}) 자수 초과: {actual}/{qlimit}",
                file=sys.stderr,
            )
            sys.exit(1)

        # 1) 헤더 자수 갱신
        new_header = f"<hp:t>{qnum}. {qtitle} {actual}/{qlimit}</hp:t>"
        xml = xml[: q.start()] + new_header + xml[q.end() :]

        # 2) 헤더 다음의 빈 run 한 곳에 답변 삽입
        # 헤더 바로 뒤 첫 번째 `<hp:run charPrIDRef="0"/>` (자기 자신 닫힘 태그) 를 답변 run 으로 교체
        cursor = q.start() + len(new_header)
        empty_run = '<hp:run charPrIDRef="0"/>'
        idx = xml.find(empty_run, cursor)
        if idx == -1:
            print(
                f"[WARN] Q{qnum} 답변 자리 (빈 run) 미발견 -- skip 삽입",
                file=sys.stderr,
            )
            continue
        filled_run = (
            f'<hp:run charPrIDRef="0"><hp:t>{escape_xml(atext)}</hp:t></hp:run>'
        )
        xml = xml[:idx] + filled_run + xml[idx + len(empty_run) :]

    return xml


def fill_hwpx(form_path: Path, answers: dict[str, str], output_path: Path) -> None:
    if not form_path.exists():
        print(f"[ERR] 원본 양식 없음: {form_path}", file=sys.stderr)
        sys.exit(2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(form_path, output_path)

    # 원본 zip 읽기 -> section0.xml 만 교체 -> 새 zip 저장
    with zipfile.ZipFile(form_path, "r") as zin:
        items = {name: zin.read(name) for name in zin.namelist()}

    section_key = "Contents/section0.xml"
    if section_key not in items:
        print(f"[ERR] {section_key} 미발견", file=sys.stderr)
        sys.exit(2)

    section_xml = items[section_key].decode("utf-8")
    filled_xml = fill_section_xml(section_xml, answers)
    items[section_key] = filled_xml.encode("utf-8")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
        # mimetype 은 STORED (압축 없이) 가 HWPX 표준
        if "mimetype" in items:
            zi = zipfile.ZipInfo("mimetype")
            zi.compress_type = zipfile.ZIP_STORED
            zout.writestr(zi, items["mimetype"])
        for name, data in items.items():
            if name == "mimetype":
                continue
            zout.writestr(name, data)

    print(f"[OK] {output_path} 작성 완료", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(description="HWPX 자소서 양식 채우기")
    ap.add_argument("--form", required=True, type=Path, help="원본 HWPX 양식 경로")
    ap.add_argument(
        "--answers",
        required=True,
        type=Path,
        help="JSON 파일 ({\"q1\": \"...\", \"q2\": \"...\", ...})",
    )
    ap.add_argument("--output", required=True, type=Path, help="결과 HWPX 출력 경로")
    args = ap.parse_args()

    answers = json.loads(args.answers.read_text(encoding="utf-8"))
    fill_hwpx(args.form, answers, args.output)


if __name__ == "__main__":
    main()
