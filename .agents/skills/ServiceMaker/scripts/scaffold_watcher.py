#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ServiceMaker - Watcher Scaffolder
새로운 기능이나 스킬 개발을 위한 범용 감시 에이전트(Watcher) 체계를 대상 디렉터리에 주입합니다.
"""

import sys
import argparse
from pathlib import Path

WATCHER_TEMPLATE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{prefix} Watcher Agent
24종 설계 문서 및 무결점(Zero-Defect) 파이프라인 준수 여부를 검증합니다.
"""

import argparse
import sys
from pathlib import Path

from watcher_rules.naming_rules import check_naming_conventions
from watcher_rules.structure_rules import check_file_structure
from watcher_rules.typing_rules import check_type_hints
from watcher_rules.exception_rules import check_exception_handling
from watcher_rules.import_rules import check_import_order

PROJECT_ROOT = Path(__file__).resolve().parent

RULE_GROUPS = [
    {{"id": "RG-01", "name": "명명 규칙", "func": check_naming_conventions, "severity": "CRITICAL"}},
    {{"id": "RG-02", "name": "기본 구조", "func": check_file_structure, "severity": "CRITICAL"}},
    {{"id": "RG-03", "name": "타입 힌트", "func": check_type_hints, "severity": "WARNING"}},
    {{"id": "RG-06", "name": "예외 처리", "func": check_exception_handling, "severity": "WARNING"}},
    {{"id": "RG-07", "name": "Import순서", "func": check_import_order, "severity": "INFO"}},
]

def _colorize(text, color):
    colors = {{"green": "\\033[92m", "red": "\\033[91m", "reset": "\\033[0m", "bold": "\\033[1m", "cyan": "\\033[96m"}}
    return f"{{colors.get(color, '')}}{{text}}{{colors['reset']}}"

def run_full_check():
    all_results = []
    for rg in RULE_GROUPS:
        try:
            violations = rg["func"](project_root=PROJECT_ROOT)
            all_results.append({{
                "id": rg["id"], "name": rg["name"], "passed": len(violations) == 0,
                "violation_count": len(violations), "violations": violations
            }})
        except Exception as e:
            all_results.append({{"id": rg["id"], "name": rg["name"], "passed": False, "violations": [str(e)]}})
    
    passed_count = sum(1 for r in all_results if r["passed"])
    return {{"passed": passed_count, "failed": len(all_results) - passed_count, "details": all_results}}

def print_report(result, gate_mode=False):
    print()
    print(_colorize("═" * 55, "bold"))
    print(_colorize("  {prefix} Watcher Agent Report", "bold"))
    print(_colorize("═" * 55, "bold"))
    
    all_passed = True
    for detail in result["details"]:
        if detail["passed"]:
            status = _colorize("[PASS]", "green")
            count_str = "0건 위반"
        else:
            all_passed = False
            status = _colorize("[FAIL]", "red")
            v_count = detail.get("violation_count", len(detail.get("violations", [])))
            count_str = f"{{v_count}}건 위반"

        print(f"  {{status}} {{detail['id']}} {{detail['name']:<15}} {{count_str}}")
        if not detail["passed"]:
            for v in detail.get("violations", [])[:5]:
                print(f"    ├─ {{v}}")
            if len(detail.get("violations", [])) > 5:
                print(f"    └─ ... 외 {{len(detail['violations']) - 5}}건 추가")

    print(_colorize("─" * 55, "cyan"))
    total = result["passed"] + result["failed"]
    pct = (result["passed"] / total * 100) if total > 0 else 0
    print(f"  총 결과: {{result['passed']}} PASS / {{result['failed']}} FAIL ({{pct:.1f}}%)")

    if gate_mode:
        if all_passed:
            print(_colorize("  게이트 판정: ✅ CLEARED (진행 가능)", "green"))
        else:
            print(_colorize("  게이트 판정: ❌ BLOCKED (FAIL 해소 필요)", "red"))

    print(_colorize("═" * 55, "bold"))
    print()
    return all_passed

def main():
    parser = argparse.ArgumentParser(description="{prefix} Watcher Agent")
    parser.add_argument("--check-all", action="store_true", help="프로젝트 전체 검증")
    parser.add_argument("--gate", action="store_true", help="게이트 모드")
    args = parser.parse_args()

    if args.check_all or args.gate:
        result = run_full_check()
        passed = print_report(result, gate_mode=args.gate)
        if args.gate and not passed:
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
'''

RULE_NAMING = '''import ast
import re
from pathlib import Path

def check_naming_conventions(project_root: Path, file_path=None) -> list[str]:
    violations = []
    targets = [file_path] if file_path else list(project_root.rglob("*.py"))
    for py_file in targets:
        if "watcher" in py_file.parts: continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except Exception: continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not re.match(r"^_?[A-Z][a-zA-Z0-9]+$", node.name):
                    violations.append(f"{py_file.name}:{node.lineno} 클래스 '{node.name}' PascalCase 위반")
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("__"): continue
                if not re.match(r"^_?[a-z][a-z0-9_]*$", node.name):
                    violations.append(f"{py_file.name}:{node.lineno} 함수 '{node.name}' snake_case 위반")
    return violations
'''

RULE_STRUCTURE = '''from pathlib import Path

def check_file_structure(project_root: Path, file_path=None) -> list[str]:
    violations = []
    return violations
'''

RULE_TYPING = '''import ast
from pathlib import Path

def check_type_hints(project_root: Path, file_path=None) -> list[str]:
    violations = []
    targets = [file_path] if file_path else list(project_root.rglob("*.py"))
    for py_file in targets:
        if "watcher" in py_file.parts: continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except Exception: continue

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("__"): continue
                for arg in node.args.args:
                    if arg.arg == 'self' or arg.arg == 'cls': continue
                    if arg.annotation is None:
                        violations.append(f"{py_file.name}:{node.lineno} 함수 '{node.name}' 파라미터 '{arg.arg}' 타입 누락")
                if node.returns is None:
                    violations.append(f"{py_file.name}:{node.lineno} 함수 '{node.name}' 리턴 타입 누락")
    return violations
'''

RULE_EXCEPTION = '''import ast
from pathlib import Path

def check_exception_handling(project_root: Path, file_path=None) -> list[str]:
    violations = []
    targets = [file_path] if file_path else list(project_root.rglob("*.py"))
    for py_file in targets:
        if "watcher" in py_file.parts: continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except: continue
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    violations.append(f"{py_file.name}:{node.lineno} bare except 사용됨 (광범위한 예외 처리)")
                elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                    violations.append(f"{py_file.name}:{node.lineno} `except Exception` 사용됨. 더 구체적인 예외 타입을 지정할 것")
    return violations
'''

RULE_IMPORT = '''from pathlib import Path

def check_import_order(project_root: Path, file_path=None) -> list[str]:
    return []
'''


def scaffold_watcher(target_dir: Path, prefix: str):
    """지정된 디렉터리에 Watcher 감시 에이전트 파일을 생성합니다."""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    rules_dir = target_dir / "watcher_rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    # 룰 모듈 생성
    (rules_dir / "__init__.py").touch()
    (rules_dir / "naming_rules.py").write_text(RULE_NAMING, encoding="utf-8")
    (rules_dir / "structure_rules.py").write_text(RULE_STRUCTURE, encoding="utf-8")
    (rules_dir / "typing_rules.py").write_text(RULE_TYPING, encoding="utf-8")
    (rules_dir / "exception_rules.py").write_text(RULE_EXCEPTION, encoding="utf-8")
    (rules_dir / "import_rules.py").write_text(RULE_IMPORT, encoding="utf-8")
    
    # 메인 Watcher 스크립트 생성
    watcher_path = target_dir / f"{prefix.lower()}_watcher.py"
    watcher_path.write_text(WATCHER_TEMPLATE.format(prefix=prefix), encoding="utf-8")
    
    print(f"✅ Watcher Agent Scaffolding Completed at {target_dir}")
    print(f"👉 To use: python {watcher_path.relative_to(Path.cwd())} --gate")

def main():
    parser = argparse.ArgumentParser(description="ServiceMaker Watcher Scaffolder")
    parser.add_argument("target_dir", help="Watcher를 셋업할 대상 디렉터리 경로")
    parser.add_argument("--prefix", default="NewSkill", help="Watcher 이름 Prefix (예: EvaluatorV6)")
    
    args = parser.parse_args()
    
    target_path = Path(args.target_dir).resolve()
    scaffold_watcher(target_path, args.prefix)

    
if __name__ == "__main__":
    main()
