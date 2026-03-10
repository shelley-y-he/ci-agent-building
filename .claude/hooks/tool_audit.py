"""
Claude Code PostToolUse hook — tool audit logger (ci-agent-building project).
Appends one row per tool call to tool_audit.log in the project root.
"""

import json
import sys
import os
from datetime import datetime

LOG_PATH = r"G:\My Drive\Colab Notebooks\ci-agent-building\tool_audit.log"

def summarize_input(tool_name, tool_input):
    """Extract the most useful short summary from each tool's input."""
    try:
        if tool_name == "Bash":
            return tool_input.get("command", "")[:200]
        elif tool_name in ("Read", "Write", "Edit"):
            return tool_input.get("file_path", "")
        elif tool_name == "Glob":
            return tool_input.get("pattern", "")
        elif tool_name == "Grep":
            return f"pattern={tool_input.get('pattern', '')} path={tool_input.get('path', '')}"
        elif tool_name == "Agent":
            subtype = tool_input.get("subagent_type", "general")
            desc = tool_input.get("description", "")
            return f"subagent_type={subtype} | {desc}"
        elif tool_name == "WebSearch":
            return tool_input.get("query", "")
        elif tool_name == "WebFetch":
            return tool_input.get("url", "")
        else:
            return json.dumps(tool_input)[:150]
    except Exception:
        return ""

def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "Unknown")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "")[:8]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = summarize_input(tool_name, tool_input)

    row = f"{timestamp} | {session_id} | {tool_name:<12} | {summary}\n"

    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(row)
    except Exception:
        pass

if __name__ == "__main__":
    main()
