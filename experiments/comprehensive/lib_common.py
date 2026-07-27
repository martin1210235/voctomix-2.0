#!/usr/bin/env python3
"""Shared helpers for the comprehensive test suite: statistics, CSV and XLSX.

CSV is the canonical, always-produced output. XLSX is a convenience bundle
built from the same rows; if it ever fails, the CSVs still hold every datum.
"""

import csv
import os
from datetime import datetime

import numpy as np


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def stats(values):
    """Descriptive statistics for a list of numbers. Empty-safe."""
    vals = [float(v) for v in values if v is not None]
    if not vals:
        return {k: None for k in
                ("n", "min", "q1", "median", "q3", "p95", "p99", "max", "mean", "std")}
    a = np.array(vals, dtype=float)
    return {
        "n": int(a.size),
        "min": round(float(np.min(a)), 3),
        "q1": round(float(np.percentile(a, 25)), 3),
        "median": round(float(np.median(a)), 3),
        "q3": round(float(np.percentile(a, 75)), 3),
        "p95": round(float(np.percentile(a, 95)), 3),
        "p99": round(float(np.percentile(a, 99)), 3),
        "max": round(float(np.max(a)), 3),
        "mean": round(float(np.mean(a)), 3),
        "std": round(float(np.std(a, ddof=1)) if a.size > 1 else 0.0, 3),
    }


def write_csv(path, fieldnames, rows):
    """Write rows (list of dicts) to a CSV. Returns path."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path


def write_summary_csv(path, summary_rows):
    """summary_rows: list of dicts, each a named metric block from stats()
    plus a 'metric' (and optional 'group') label."""
    if not summary_rows:
        return None
    fieldnames = list(summary_rows[0].keys())
    return write_csv(path, fieldnames, summary_rows)


def bundle_xlsx(xlsx_path, sheets):
    """sheets: dict {sheet_name: (fieldnames, rows)}. Best-effort; never the
    source of truth. Returns path or None on failure."""
    try:
        from openpyxl import Workbook
        wb = Workbook()
        wb.remove(wb.active)
        for name, (fieldnames, rows) in sheets.items():
            ws = wb.create_sheet(title=name[:31])
            ws.append(list(fieldnames))
            for r in rows:
                ws.append([r.get(k) for k in fieldnames])
        os.makedirs(os.path.dirname(os.path.abspath(xlsx_path)), exist_ok=True)
        wb.save(xlsx_path)
        return xlsx_path
    except Exception as e:
        print(f"[xlsx] aviso: no se pudo generar {xlsx_path}: {e} (los CSV son la fuente de verdad)")
        return None
