import os
import sys
import datetime
import re

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def append_to_1st_log(project_root, project_name, checkpoint_link):
    log_mgt_dir = os.path.join(project_root, "docs", "LogManagement")
    first_log_path = os.path.join(log_mgt_dir, "1st_Log.md")
    ensure_dir(log_mgt_dir)
    
    today = datetime.datetime.now().strftime("%y-%m-%d")
    new_row = f"| `{project_name}` | {today} | [{os.path.basename(checkpoint_link)}]({checkpoint_link}) | 🚧 진행 중 |\n"

    # Read existing 1st_Log.md
    if not os.path.exists(first_log_path):
        lines = [
            "---\n",
            f"last_updated: \"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\"\n",
            "total_lines: 20\n",
            "---\n\n",
            "# 🌐 1st_Log: 통합 상황판 (Dashboard)\n\n",
            "## 🚀 최근 활성 프로젝트 동기화 지점\n\n",
            "| 프로젝트/스킬명 | 최근 작업일 | 체크포인트 링크 | 잔여 작업 여부 |\n",
            "| :--- | :--- | :--- | :--- |\n"
        ]
        with open(first_log_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    with open(first_log_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    print(f"  [DEBUG] Read {len(lines)} lines from 1st_Log.md")
        
    # Find table insertion point or update existing project
    table_idx = -1
    project_idx = -1
    last_data_row = -1
    
    for i, line in enumerate(lines):
        # Flexible header matching (handles both short and long column names)
        if "프로젝트" in line and "스킬명" in line and line.strip().startswith("|"):
            table_idx = i + 2  # below header and separator
        # Track existing project row
        if f"`{project_name}`" in line:
            project_idx = i
        # Track the last table data row (starts with | but is not header/separator)
        if table_idx != -1 and i >= table_idx and line.strip().startswith("|"):
            last_data_row = i
            
    if project_idx != -1:
        # Update existing
        lines[project_idx] = new_row
    elif table_idx != -1:
        # Insert after the last data row, or at table_idx if no data rows
        insert_at = (last_data_row + 1) if last_data_row != -1 else table_idx
        lines.insert(insert_at, new_row)
        print(f"  [DEBUG] Inserted new row at line {insert_at}")
    else:
        # Append at end if table is broken
        lines.append("\n## 🚀 최근 활성 프로젝트 동기화 지점\n")
        lines.append("| 프로젝트/스킬명 | 최근 작업일 | 체크포인트 링크 | 잔여 작업 여부 |\n")
        lines.append("| :--- | :--- | :--- | :--- |\n")
        lines.append(new_row)
        
    # Update total_lines
    total_lines = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("total_lines:"):
            lines[i] = f"total_lines: {total_lines}\n"
        if line.startswith("last_updated:"):
            lines[i] = f"last_updated: \"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\"\n"
            
    # Check for rotation
    if total_lines > 500:
        archive_name = f"1st_Log_archived_{datetime.datetime.now().strftime('%y%m%d_%H%M')}.md"
        os.rename(first_log_path, os.path.join(log_mgt_dir, archive_name))
        
        # Create new 1st_Log with minimal lines and add reference
        new_lines = [
            "---\n",
            f"last_updated: \"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\"\n",
            "total_lines: 22\n",
            "---\n\n",
            "# 🌐 1st_Log: 통합 상황판 (Dashboard)\n\n",
            "## 🚀 최근 활성 프로젝트 동기화 지점\n\n",
            "| 프로젝트/스킬명 | 최근 작업일 | 체크포인트 링크 | 잔여 작업 여부 |\n",
            "| :--- | :--- | :--- | :--- |\n",
            new_row,
            "\n## 📦 아카이브 링크 (Archived Logs)\n",
            f"- [{archive_name} 아카이브 보기](./{archive_name})\n"
        ]
        with open(first_log_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"[Success] 1st_Log rotated to {archive_name}")
    else:
        with open(first_log_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            f.flush()
            os.fsync(f.fileno())
        print("[Success] 1st_Log updated successfully.")

def run_handoff(project_path, goal_text, distilled_actions, current_result, next_steps, qa_history_file=None):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    
    # 1. Ensure target Log directory exists via strict governance
    log_dir = os.path.join(project_path, "Log")
    ensure_dir(log_dir)
    
    project_name = os.path.basename(os.path.normpath(project_path))
    
    # 2. Determine next session log file name
    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M")
    session_file = f"session_{timestamp}.md"
    session_path = os.path.join(log_dir, session_file)
    
    # 3. Write Yaml Template
    yaml_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    content = f"""---
date: "{yaml_date}"
project: "{project_name}"
tags: ["session-handoff", "auto-generated"]
status: "in-progress"
---

# Session Context Checkpoint

## 1. 세션 목표 (Goal)
{goal_text}

## 2. 지식 증류 및 수행 내역 (Distilled Actions)
{distilled_actions}

## 3. 도출 결과 (Current Result)
{current_result}

## 4. 다음 AI를 위한 남은 과제 (Next Steps)
{next_steps}
"""

    # 3.5 Read QA History
    qa_history_content = ""
    if qa_history_file and os.path.exists(qa_history_file):
        try:
            with open(qa_history_file, 'r', encoding='utf-8') as qf:
                qa_history_content = qf.read()
            os.remove(qa_history_file)
            content += f"\n## 5. 상세 대화 히스토리 (Q&A Pairs)\n{qa_history_content}\n"
        except Exception as e:
            print(f"[Warning] Failed to read QA history file: {e}")

    content += f"""
---
*통합 관리 링크*: [1st_Log로 돌아가기]({"../../docs/LogManagement/1st_Log.md" if "Projects" in project_path else "../../../docs/LogManagement/1st_Log.md"})
"""

    with open(session_path, "w", encoding='utf-8') as f:
        f.write(content)
        
    print(f"[Success] Local session log saved: {session_path}")
    
    # 4. Integrate with 1st_Log
    # Calculate relative link for 1st_Log
    log_mgt_dir = os.path.join(project_root, "docs", "LogManagement")
    rel_link = os.path.relpath(session_path, log_mgt_dir).replace('\\', '/')
    
    append_to_1st_log(project_root, project_name, rel_link)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python handoff.py <project_path> <goal> <distilled> <result> <next_steps> [qa_history_file]")
        sys.exit(1)
        
    qa_file = sys.argv[6] if len(sys.argv) > 6 else None
    run_handoff(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], qa_file)
