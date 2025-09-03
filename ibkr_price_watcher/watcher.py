from __future__ import annotations

import time
from typing import Dict, Any, Optional, List

from ib_insync import IB, util, Stock, Contract
from .discord_client import post_discord

class PriceWatcher:
    def __init__(self, ib: IB, cfg: Dict[str, Any], symbols: Dict[str, Dict[str, Any]]):
        self.ib = ib
        self.cfg = cfg
        self.symbols = symbols
        self.last_sent_price: Dict[str, float] = {}
        self.last_sent_time: Dict[str, float] = {}

    # ---------- helpers ----------

    def _passes_thresholds(self, sym: str, new_price: float) -> bool:
        prev = self.last_sent_price.get(sym)
        if prev is None:
            return True  # first tick

        s_cfg = self.symbols[sym]
        dfl = self.cfg.get("defaults", {})
        min_abs = float(s_cfg.get("min_change_abs", dfl.get("min_change_abs", 0.0)))
        min_pct = float(s_cfg.get("min_change_pct", dfl.get("min_change_pct", 0.0)))

        abs_change = abs(new_price - prev)
        pct_change = (abs_change / prev * 100.0) if prev else 0.0

        if abs_change < min_abs:
            return False
        if min_pct > 0.0 and pct_change < min_pct:
            return False
        return True

    def _throttled(self, sym: str) -> bool:
        throttle = float(self.cfg.get("throttle_seconds", 0))
        if throttle <= 0:
            return False
        last_t = self.last_sent_time.get(sym, 0.0)
        return (time.time() - last_t) < throttle

    def _symbol_label(self, sym: str) -> str:
        nick = self.symbols[sym].get("nickname")
        return f"{nick} ({sym})" if nick else sym

    # ---------- tick handler ----------

    def on_tick(self, ticker) -> None:
        sym = ticker.contract.symbol
        last = ticker.last
        if last is None:
            last = ticker.marketPrice()
        if last is None or last != last:  # None or NaN
            return

        if not self._passes_thresholds(sym, last):
            return
        if self._throttled(sym):
            return

        self.last_sent_price[sym] = last
        self.last_sent_time[sym] = time.time()

        content = f"💹 **{self._symbol_label(sym)}** last price: **{last:.4f}**"
        webhook = self.cfg["discord"]["webhook_url"]
        if webhook:
            post_discord(webhook, content, username="IBKR Price Watcher")
        print(content)

# ---------- assembly / run ----------

async def run_async(cfg: Dict[str, Any], symbols: Dict[str, Dict[str, Any]]) -> None:
    """
    Connect to IBKR, subscribe to market data, and dispatch to PriceWatcher.
    """
    if not symbols:
        print("[WARN] No symbols loaded; exiting.")
        return

    ib = IB()
    print(f"[INFO] Connecting to IB {cfg['ib']['host']}:{cfg['ib']['port']} (clientId={cfg['ib']['clientId']}) ...")
    await ib.connectAsync(cfg["ib"]["host"], cfg["ib"]["port"], clientId=cfg["ib"]["clientId"])

    use_delayed = cfg["ib"].get("useDelayed", False)
    if use_delayed:
        # 1=Live, 2=Frozen, 3=Delayed, 4=Delayed/Frozen
        ib.reqMarketDataType(3)
        print("[INFO] Using delayed market data")

    watcher = PriceWatcher(ib, cfg, symbols)

    # Build IB contracts
    contracts: List[Contract] = []
    for sym, s_cfg in symbols.items():
        if s_cfg.get("secType", "STK").upper() == "STK":
            c = Stock(symbol=sym, exchange=s_cfg.get("exchange", "SMART"), currency=s_cfg.get("currency", "USD"))
        else:
            c = Contract()
            c.symbol = sym
            c.secType = s_cfg.get("secType", "STK")
            c.exchange = s_cfg.get("exchange", "SMART")
            c.currency = s_cfg.get("currency", "USD")
        contracts.append(c)

    qualified = await ib.qualifyContractsAsync(*contracts)

    # Request market data streams
    _ = [ib.reqMktData(c, "", False, False) for c in qualified]

    # Hook event for batched tick delivery
    def on_pending_tickers(ticks):
        for t in ticks:
            try:
                watcher.on_tick(t)
            except Exception as e:
                print(f"[WARN] on_tick error for {t.contract.symbol}: {e}")

    ib.pendingTickersEvent += on_pending_tickers

    try:
        print("[INFO] Listening for price updates. Ctrl+C to stop.")
        while True:
            await util.sleep(1.0)
    finally:
        ib.disconnect()
