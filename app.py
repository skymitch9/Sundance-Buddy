from __future__ import annotations

from ib_insync import util
from ibkr_price_watcher.config import load_config
from ibkr_price_watcher.symbols import load_symbols
from ibkr_price_watcher.watcher import run_async

def _main():
    cfg = load_config()
    symbols = load_symbols(cfg["paths"]["symbols_dir"])

    if not cfg["discord"]["webhook_url"]:
        print("[WARN] No Discord webhook configured; messages will only print to console.")

    util.run(run_async(cfg, symbols))

if __name__ == "__main__":
    _main()
