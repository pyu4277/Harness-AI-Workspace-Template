#!/usr/bin/env python3
"""
daemon-5min.py -- 5분 간격 wiki 상태 점검 + graph 재빌드
Reference-Port: MindVault 5-min daemon 수치만 차용 (schedule 라이브러리 사용)

사용자가 명시적으로 실행. `--once` 플래그로 1회 tick 만 smoke 테스트.
"""
import sys
import time
import subprocess
import os
from pathlib import Path


def run_tick():
    project_root = Path(__file__).resolve().parents[4]  # scripts → llm-wiki → skills → .agents → project
    build = project_root / ".agents" / "skills" / "llm-wiki" / "scripts" / "graph" / "graph-build.py"
    if not build.exists():
        return {"ok": False, "reason": "graph-build.py not found"}
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        r = subprocess.run([sys.executable, str(build)],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           timeout=60, env=env)
        return {"ok": r.returncode == 0, "stdout": (r.stdout or "")[:200]}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def main():
    once = "--once" in sys.argv
    try:
        import schedule  # noqa: F401
    except ImportError:
        print("ERROR: schedule not installed", file=sys.stderr)
        sys.exit(1)

    if once:
        r = run_tick()
        print(r)
        return

    import schedule
    schedule.every(5).minutes.do(run_tick)
    print("[daemon-5min] started (5-minute interval)", flush=True)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
