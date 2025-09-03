from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

def load_symbols(symbols_dir: str | Path) -> Dict[str, Dict[str, Any]]:
    """
    Load one JSON per symbol from `symbols_dir`. Keys are uppercased symbols.
    """
    p = Path(symbols_dir)
    p.mkdir(parents=True, exist_ok=True)

    out: Dict[str, Dict[str, Any]] = {}
    for f in p.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sym = str(data.get("symbol", "")).strip().upper()
            if not sym:
                print(f"[WARN] {f.name} missing 'symbol', skipping")
                continue
            # sane defaults
            data.setdefault("exchange", "SMART")
            data.setdefault("currency", "USD")
            data.setdefault("secType", "STK")
            out[sym] = data
        except Exception as e:
            print(f"[WARN] Failed reading {f.name}: {e}")

    if not out:
        print("[WARN] No symbols found. Add JSON files like AAPL.json to your symbols directory.")

    return out
