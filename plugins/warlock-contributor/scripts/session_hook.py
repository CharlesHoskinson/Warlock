#!/usr/bin/env python3
"""Read-only advisory hook; never denies a prompt, tool, or correction loop."""
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            return
        event = payload.get("hook_event_name", payload.get("hookEventName"))
        if event not in ("SessionStart", "UserPromptSubmit"):
            return
        if os.environ.get("GROK_HOOK_EVENT") or os.environ.get("GROK_PLUGIN_ROOT"):
            # Passive Grok stdout is ignored; skill/direct loop checks carry policy.
            return
        cwd = payload.get("cwd", payload.get("workspaceRoot"))
        if not isinstance(cwd, str):
            return
        location = Path(cwd).resolve()
        root = next((p for p in (location, *location.parents)
                     if (p / "docs/warlock-build-loop/v2/STATE.json").is_file()
                     and (p / "docs/elm-roadmap/requirements.json").is_file()), None)
        if root is None:
            return
        checker = Path(__file__).resolve().with_name("warlock.py")
        result = subprocess.run([sys.executable, "-B", str(checker), "--repo", str(root),
                                 "--json", "check"], capture_output=True, text=True, timeout=5)
        # Do not inject paths, prompt text, or arbitrary checker output into instructions.
        state = "passed" if result.returncode == 0 else "needs attention"
        if event == "UserPromptSubmit" and result.returncode == 0:
            return
        context = ("Warlock contribution checker " + state + ". For Warlock code use the "
                   "warlock-contribute skill, follow docs/warlock-build-loop/v2/INSTRUCTIONS.md, "
                   "and call the checker explicitly before implementation and before reporting. "
                   "Fix findings within the selected product slice. Structural compliance does "
                   "not establish original GUI/native/AT acceptance. Unrelated work may continue.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                                 "additionalContext": context}}))
    except Exception:
        # Explicit loop/CLI checks enforce the contract. A session reminder is advisory.
        return


if __name__ == "__main__":
    main()
