#!/usr/bin/env python3
"""
watch-daemon.py -- watchdog 기반 Wiki 변화 감지
Reference-Port: MindVault 5분 daemon 아이디어 (즉시 반응형 버전)

사용자가 명시적으로 실행 — SessionStart 등 기존 훅과 충돌 방지.
  python watch-daemon.py [--once]
"""
import sys
import time
from pathlib import Path


def find_wiki_root():
    import os
    env = os.environ.get("WIKI_ROOT")
    return Path(env).resolve() if env else (Path.cwd().parent / "001_Wiki_AI").resolve()


def main():
    once = "--once" in sys.argv

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("ERROR: watchdog not installed", file=sys.stderr)
        sys.exit(1)

    root = find_wiki_root()
    if not root.exists():
        print(f"ERROR: WIKI_ROOT not found: {root}", file=sys.stderr)
        sys.exit(1)

    class H(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.is_directory:
                return
            if ".obsidian" in event.src_path:
                return
            print(f"[watch] {event.event_type} {event.src_path}", flush=True)

    obs = Observer()
    obs.schedule(H(), str(root), recursive=True)
    obs.start()
    print(f"[watch-daemon] watching {root}", flush=True)

    if once:
        # smoke-test: 0.5 초 돌고 정상 종료
        time.sleep(0.5)
        obs.stop()
        obs.join(timeout=2)
        print("[watch-daemon] once-mode exit", flush=True)
        return

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


if __name__ == "__main__":
    main()
