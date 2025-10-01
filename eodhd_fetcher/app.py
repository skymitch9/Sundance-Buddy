from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Dict

from eodhd.client import EODHDClient
from eodhd.service import fetch_for_ticker
from utils.config_loader import load_config, filename_from_template, AppConfig, ConfigError
from utils.io_utils import ensure_dir, write_rows
from utils import log_utils as log


def run(config_path: Path) -> int:
    try:
        cfg: AppConfig = load_config(config_path)
    except ConfigError as e:
        log.error(str(e))
        return 2

    ensure_dir(cfg.out_dir)

    client = EODHDClient(
        api_token=cfg.api_token,
        timeout=cfg.timeout,
        max_retries=cfg.max_retries,
        backoff_base=cfg.backoff_base,
    )

    all_rows: List[Dict] = []
    errors: List[str] = []

    for ticker in cfg.tickers:
        try:
            rows = fetch_for_ticker(
                client,
                ticker=ticker,
                fdate=cfg.date_from,
                tdate=cfg.date_to,
                period=cfg.period,
                order=cfg.order,
                adjusted=cfg.adjusted,
            )
            if rows:
                if cfg.per_ticker:
                    out_name = filename_from_template(
                        cfg.filename_template, ticker, cfg.date_from, cfg.date_to, cfg.out_format
                    )
                    out_path = cfg.out_dir / out_name
                    write_rows(rows, out_path, cfg.out_format)
                    log.info(f"{ticker}: wrote {len(rows)} rows -> {out_path}")
                else:
                    if cfg.include_ticker_col:
                        for r in rows:
                            r["ticker"] = ticker
                    all_rows.extend(rows)
            else:
                log.warn(f"{ticker}: no data returned.")
        except Exception as e:
            msg = f"{ticker}: {e}"
            errors.append(msg)
            log.error(msg)

    if not cfg.per_ticker:
        out_name = filename_from_template(
            cfg.combined_filename, "combined", cfg.date_from, cfg.date_to, cfg.out_format
        )
        out_path = cfg.out_dir / out_name
        write_rows(all_rows, out_path, cfg.out_format)
        log.info(f"Combined: wrote {len(all_rows)} rows -> {out_path}")

    if errors:
        log.warn("\nFinished with some errors:\n- " + "\n- ".join(errors))
        return 1 if len(errors) == len(cfg.tickers) else 0

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Config-driven EODHD fetcher")
    parser.add_argument("--config", required=True, help="Path to JSON config file")
    args = parser.parse_args()
    sys.exit(run(Path(args.config)))
