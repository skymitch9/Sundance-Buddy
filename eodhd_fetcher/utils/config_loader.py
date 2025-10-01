from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass
class AppConfig:
    api_token: str
    tickers: List[str]
    date_from: str
    date_to: str
    period: str
    order: str
    adjusted: Optional[int]
    timeout: int
    max_retries: int
    backoff_base: float
    out_dir: Path
    out_format: str
    per_ticker: bool
    filename_template: str
    combined_filename: str
    include_ticker_col: bool


class ConfigError(ValueError):
    pass


def _valid_date(s: str) -> str:
    # Basic format check YYYY-MM-DD
    import datetime as dt
    try:
        dt.datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        raise ConfigError(f"Invalid date: {s}. Use YYYY-MM-DD.")


def _sanitize_filename(s: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


def filename_from_template(template: str, ticker: str, f: str, t: str, ext: str) -> str:
    return template.format(
        ticker=_sanitize_filename(ticker),
        **{"from": f, "to": t, "ext": ext}
    )


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        raise ConfigError(f"Config not found: {config_path}")

    try:
        cfg: Dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ConfigError(f"Failed to parse JSON config: {e}")

    # API token comes from env
    api_token = os.getenv("EODHD_API_TOKEN")
    if not api_token:
        raise ConfigError("EODHD_API_TOKEN is missing. Add it to your .env or environment.")

    # Required
    tickers = cfg.get("tickers")
    if not isinstance(tickers, list) or not tickers:
        raise ConfigError("'tickers' must be a non-empty list of strings.")

    fdate = _valid_date(str(cfg.get("from")))
    tdate = _valid_date(str(cfg.get("to")))
    if fdate > tdate:
        raise ConfigError("'from' must be <= 'to'.")

    # Data
    data = {"period": "d", "order": "a", "adjusted": None}
    data.update(cfg.get("data", {}))

    period = str(data.get("period", "d")).lower()
    if period not in ("d", "w", "m"):
        raise ConfigError("data.period must be one of: d, w, m")
    order = str(data.get("order", "a")).lower()
    if order not in ("a", "d"):
        raise ConfigError("data.order must be one of: a, d")

    adjusted_raw = data.get("adjusted", None)
    adjusted = None
    if adjusted_raw is not None:
        try:
            adjusted = int(adjusted_raw)
            if adjusted not in (0, 1):
                raise ValueError
        except Exception:
            raise ConfigError("data.adjusted must be 0 or 1 if provided")

    # Requests
    req = {"timeout": 30, "max_retries": 5, "backoff_base": 0.8}
    req.update(cfg.get("requests", {}))

    # Output
    out_cfg = {
        "directory": "./outputs",
        "format": "csv",
        "per_ticker": True,
        "filename_template": "{ticker}_{from}_{to}.{ext}",
        "combined_filename": "combined_{from}_{to}.{ext}",
        "include_ticker_column_in_combined": True,
    }
    out_cfg.update(cfg.get("output", {}))

    out_dir = Path(str(out_cfg["directory"]))
    out_format = str(out_cfg["format"]).lower()
    if out_format not in ("csv", "parquet", "json"):
        raise ConfigError("output.format must be csv, parquet, or json")

    return AppConfig(
        api_token=api_token,
        tickers=[str(t).strip() for t in tickers],
        date_from=fdate,
        date_to=tdate,
        period=period,
        order=order,
        adjusted=adjusted,
        timeout=int(req["timeout"]),
        max_retries=int(req["max_retries"]),
        backoff_base=float(req["backoff_base"]),
        out_dir=out_dir,
        out_format=out_format,
        per_ticker=bool(out_cfg["per_ticker"]),
        filename_template=str(out_cfg["filename_template"]),
        combined_filename=str(out_cfg["combined_filename"]),
        include_ticker_col=bool(out_cfg["include_ticker_column_in_combined"]),
    )
