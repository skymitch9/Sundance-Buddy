from __future__ import annotations
from typing import Dict, List
from .client import EODHDClient


def fetch_for_ticker(
	client: EODHDClient,
	ticker: str,
	fdate: str,
	tdate: str,
	period: str,
	order: str,
	adjusted: int | None,
) -> List[Dict]:
	rows = client.get_eod(
		ticker=ticker,
		date_from=fdate,
		date_to=tdate,
		period=period,
		order=order,
		adjusted=adjusted,
	)
	# Ensure 'date' is the first column if present
	if rows:
		keys = list(rows[0].keys())
		if "date" in keys:
			keys = ["date"] + [k for k in keys if k != "date"]
		rows = [{k: r.get(k) for k in keys} for r in rows]
	return rows