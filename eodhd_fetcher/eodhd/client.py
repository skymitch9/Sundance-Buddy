from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

EODHD_BASE = "https://eodhistoricaldata.com/api/eod/{ticker}"


@dataclass
class EODHDClient:
    api_token: str
    timeout: int = 30
    max_retries: int = 5
    backoff_base: float = 0.8  # seconds

    def _request(self, url: str, params: Dict[str, Any]) -> requests.Response:
        sess = requests.Session()
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = sess.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp
                if resp.status_code in (429, 500, 502, 503, 504):
                    wait = self.backoff_base * (2 ** attempt)
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait = max(wait, float(retry_after))
                        except Exception:
                            pass
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
            except Exception as exc:
                last_exc = exc
                time.sleep(self.backoff_base * (2 ** attempt))
        if last_exc:
            raise last_exc
        raise RuntimeError("Unexpected request error without exception")

    def get_eod(
        self,
        ticker: str,
        date_from: str,
        date_to: str,
        period: str = "d",
        order: str = "a",
        adjusted: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        url = EODHD_BASE.format(ticker=ticker)
        params: Dict[str, Any] = {
            "from": date_from,
            "to": date_to,
            "period": period,
            "order": order,
            "api_token": self.api_token,
            "fmt": "json",
        }
        if adjusted is not None:
            params["adjusted"] = adjusted
        resp = self._request(url, params=params)
        data = resp.json()
        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(f"EODHD API error: {data.get('error')}")
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected JSON shape: {data}")
        return data
