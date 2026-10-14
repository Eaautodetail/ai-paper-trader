"""Start/stop switch, stored in control/state.json and changed only by the "Control" workflow.

While a session runs, the trading job re-reads this file from GitHub every poll, so
pressing Stop takes effect within about a minute.
"""
import json
import subprocess
from pathlib import Path

DEFAULT = {"evaluation_enabled": False, "stop_requested": False, "rehearsal_date": None}


def read_local(root: Path) -> dict:
    p = root / "control" / "state.json"
    if not p.exists():
        return dict(DEFAULT)
    return {**DEFAULT, **json.loads(p.read_text())}


def read_remote(root: Path, branch: str = "main") -> dict:
    """Latest control state from GitHub; falls back to the local copy if git is unavailable."""
    try:
        subprocess.run(["git", "fetch", "-q", "origin", branch], cwd=root, check=True, timeout=30,
                       capture_output=True)
        out = subprocess.run(["git", "show", f"origin/{branch}:control/state.json"], cwd=root, check=True,
                             timeout=10, capture_output=True, text=True).stdout
        return {**DEFAULT, **json.loads(out)}
    except Exception:
        return read_local(root)


def write(root: Path, **changes) -> dict:
    state = {**read_local(root), **changes}
    p = root / "control" / "state.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(state, indent=2) + "\n")
    return state
