from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

# Project root = package parent
PKG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PKG_DIR.parent

# load environment from .env files if present (do not override real env)
def _load_env_files() -> None:
    for name in (".env", ".env.local"):
        p = PROJECT_ROOT / name
        if p.exists():
            # override=False means REAL env vars win over .env entries
            load_dotenv(dotenv_path=str(p), override=False)

_load_env_files()

def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "y", "on")

def load_config() -> Dict[str, Any]:
    """
    Load configuration from PROJECT_ROOT/config.yaml with env var overrides.
    .env (if present) is loaded at import time.
    """
    cfg_path = PROJECT_ROOT / "config.yaml"
    file_cfg: Dict[str, Any] = {}
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            file_cfg = yaml.safe_load(f) or {}

    ib_cfg = file_cfg.get("ib", {})
    discord_cfg = file_cfg.get("discord", {})
    defaults_cfg = file_cfg.get("defaults", {})

    merged: Dict[str, Any] = {
        "ib": {
            "host": os.getenv("IB_HOST", ib_cfg.get("host", "127.0.0.1")),
            "port": int(os.getenv("IB_PORT", ib_cfg.get("port", 7497))),
            "clientId": int(os.getenv("IB_CLIENT_ID", ib_cfg.get("clientId", 1001))),
            "useDelayed": _env_bool("IB_USE_DELAYED", ib_cfg.get("useDelayed", False)),
        },
        "discord": {
            "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", discord_cfg.get("webhook_url", "")),
        },
        "throttle_seconds": float(os.getenv("THROTTLE_SECONDS", file_cfg.get("throttle_seconds", 2))),
        "defaults": {
            "min_change_abs": float(os.getenv("DEFAULT_MIN_CHANGE_ABS", defaults_cfg.get("min_change_abs", 0.0))),
            "min_change_pct": float(os.getenv("DEFAULT_MIN_CHANGE_PCT", defaults_cfg.get("min_change_pct", 0.0))),
        },
        # allow overriding symbols dir via env; default to PROJECT_ROOT/symbols
        "paths": {
            "symbols_dir": os.getenv("SYMBOLS_DIR", str(PROJECT_ROOT / "symbols")),
        },
    }
    return merged
