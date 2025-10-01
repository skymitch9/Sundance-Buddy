from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

try:
	import pyarrow as pa  # type: ignore
	import pyarrow.parquet as pq  # type: ignore
	_PARQUET_OK = True
except Exception:
	_PARQUET_OK = False

def ensure_dir(p: Path) -> None:
	p.mkdir(parents=True, exist_ok=True)

def write_rows(rows: List[Dict], out_path: Path, fmt: str) -> None:
	fmt = fmt.lower()
	if fmt == "parquet":
		if not _PARQUET_OK:
			raise RuntimeError("pyarrow is required for Parquet output. Install with: pip install pyarrow")
		table = pa.Table.from_pylist(rows)
		pq.write_table(table, str(out_path))
		return
	if fmt == "json":
		out_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
		return
	# CSV
	if not rows:
		out_path.write_text("", encoding="utf-8")
		return
	fieldnames = list(rows[0].keys())
	with out_path.open("w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(rows)