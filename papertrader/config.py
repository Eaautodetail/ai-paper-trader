import tomllib
from pathlib import Path

from .safety import assert_paper_only

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: Path | None = None) -> dict:
    path = path or ROOT / "config.toml"
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    assert_paper_only(cfg)
    return cfg
