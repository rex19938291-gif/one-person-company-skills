#!/usr/bin/env python3
"""Summarize direct GSC API export files created by gsc_fetch_search_analytics.py."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, Any]]:
 payload = json.loads(path.read_text(encoding="utf-8"))
 dims = payload.get("dimensions", [])
 rows = []
 for row in payload.get("result", {}).get("rows", []):
 item = {dim: key for dim, key in zip(dims, row.get("keys", []))}
 for key in ("clicks", "impressions", "ctr", "position"):
 item[key] = float(row.get(key, 0))
 rows.append(item)
 return rows


def metric_total(rows: list[dict[str, Any]]) -> dict[str, float]:
 clicks = sum(row["clicks"] for row in rows)
 impressions = sum(row["impressions"] for row in rows)
 weighted_position = (
 sum(row["position"] * row["impressions"] for row in rows) / impressions
 if impressions
 else 0
 )
 return {
 "clicks": round(clicks, 2),
 "impressions": round(impressions, 2),
 "ctr": clicks / impressions if impressions else 0,
 "position": weighted_position,
 }


def top(rows: list[dict[str, Any]], label_key: str, limit: int) -> list[dict[str, Any]]:
 return [
 {
 "label": row.get(label_key, ""),
 "clicks": row["clicks"],
 "impressions": row["impressions"],
 "ctr": row["ctr"],
 "position": row["position"],
 }
 for row in sorted(rows, key=lambda r: (r["clicks"], r["impressions"]), reverse=True)[:limit]
 ]


def rows_for(folder: Path, prefix: str, window: str) -> list[dict[str, Any]]:
 path = folder / f"{prefix}-{window}.json"
 return load_rows(path) if path.exists() else []


def bucket_queries(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
 patterns = {
 "brand": re.compile(r"(電商型客戶站|i place|電商型客戶站|愛普雷斯)", re.I),
 "local": re.compile(r"(台中|北屯|西屯|南屯|七期|台北|新竹|桃園|台南|高雄)"),
 "commercial": re.compile(r"(費用|價格|預算|推薦|規劃|方案|安裝|團購|系統|公司|品牌)"),
 "informational": re.compile(r"(是什麼|怎麼|如何|入門|教學|diy|優缺點|比較|homekit|網關|零火線|aqara|matter|thread)", re.I),
 }
 groups: dict[str, list[dict[str, Any]]] = {key: [] for key in patterns}
 groups["other"] = []
 for row in rows:
 query = str(row.get("query", ""))
 target = "other"
 for key, pattern in patterns.items():
 if pattern.search(query):
 target = key
 break
 groups[target].append(row)
 return {key: metric_total(value) | {"rows": len(value)} for key, value in groups.items()}


def compare(current: list[dict[str, Any]], previous: list[dict[str, Any]], key: str, limit: int) -> dict[str, list[dict[str, Any]]]:
 prev = {row.get(key): row for row in previous}
 changes = []
 for row in current:
 label = row.get(key)
 old = prev.get(label, {"clicks": 0, "impressions": 0, "ctr": 0, "position": 0})
 if row["impressions"] < 20 and old["impressions"] < 20:
 continue
 changes.append(
 {
 "label": label,
 "click_delta": row["clicks"] - old["clicks"],
 "impression_delta": row["impressions"] - old["impressions"],
 "current_clicks": row["clicks"],
 "current_impressions": row["impressions"],
 "current_ctr": row["ctr"],
 "current_position": row["position"],
 }
 )
 return {
 "up": sorted(changes, key=lambda row: (row["click_delta"], row["impression_delta"]), reverse=True)[:limit],
 "down": sorted(changes, key=lambda row: (row["click_delta"], row["impression_delta"]))[:limit],
 }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
 lines = [
 f"# GSC API Summary: {summary['domain']}",
 "",
 f"- Property: `{summary['property']}`",
 f"- Annual window: `{summary['annual_window']}`",
 f"- Recent window: `{summary['recent_window']}`",
 f"- Previous window: `{summary['previous_window']}`",
 "",
 "## Totals",
 "",
 "| Window | Clicks | Impressions | CTR | Avg position |",
 "|---|---:|---:|---:|---:|",
 ]
 for label, totals in summary["totals"].items():
 lines.append(
 f"| {label} | {totals['clicks']:.0f} | {totals['impressions']:.0f} | {totals['ctr']*100:.2f}% | {totals['position']:.2f} |"
 )
 for section in ("top_queries", "top_pages", "low_ctr_queries", "push_queries"):
 lines.extend(["", f"## {section}", "", "| Label | Clicks | Impressions | CTR | Avg position |", "|---|---:|---:|---:|---:|"])
 for row in summary[section]:
 lines.append(
 f"| {row['label']} | {row['clicks']:.0f} | {row['impressions']:.0f} | {row['ctr']*100:.2f}% | {row['position']:.2f} |"
 )
 path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
 parser = argparse.ArgumentParser()
 parser.add_argument("--input", required=True, help="Direct GSC API export folder")
 parser.add_argument("--domain", required=True)
 parser.add_argument("--property", required=True)
 parser.add_argument("--annual-window", required=True, help="Example: 2025-06-25_2026-06-24")
 parser.add_argument("--recent-window", required=True)
 parser.add_argument("--previous-window", required=True)
 parser.add_argument("--out-prefix", default="gsc-api-summary")
 parser.add_argument("--limit", type=int, default=20)
 args = parser.parse_args()

 folder = Path(args.input).expanduser().resolve()
 annual_queries = rows_for(folder, "queries", args.annual_window)
 annual_pages = rows_for(folder, "pages", args.annual_window)
 annual_dates = rows_for(folder, "dates", args.annual_window)
 recent_queries = rows_for(folder, "queries", args.recent_window)
 recent_pages = rows_for(folder, "pages", args.recent_window)
 recent_dates = rows_for(folder, "dates", args.recent_window)
 previous_queries = rows_for(folder, "queries", args.previous_window)
 previous_pages = rows_for(folder, "pages", args.previous_window)
 previous_dates = rows_for(folder, "dates", args.previous_window)

 low_ctr = [
 row
 for row in annual_queries
 if row["impressions"] >= 300 and row["position"] <= 10 and row["ctr"] < 0.015
 ]
 push = [
 row
 for row in annual_queries
 if row["impressions"] >= 100 and 4 <= row["position"] <= 20
 ]

 summary = {
 "domain": args.domain,
 "property": args.property,
 "annual_window": args.annual_window,
 "recent_window": args.recent_window,
 "previous_window": args.previous_window,
 "totals": {
 "annual": metric_total(annual_dates),
 "recent": metric_total(recent_dates),
 "previous": metric_total(previous_dates),
 },
 "query_buckets": bucket_queries(annual_queries),
 "top_queries": top(annual_queries, "query", args.limit),
 "top_pages": top(annual_pages, "page", args.limit),
 "low_ctr_queries": top(low_ctr, "query", args.limit),
 "push_queries": top(push, "query", args.limit),
 "query_changes": compare(recent_queries, previous_queries, "query", args.limit),
 "page_changes": compare(recent_pages, previous_pages, "page", args.limit),
 }

 json_path = folder / f"{args.out_prefix}.json"
 md_path = folder / f"{args.out_prefix}.md"
 json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
 write_markdown(summary, md_path)
 print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, ensure_ascii=False))
 return 0


if __name__ == "__main__":
 raise SystemExit(main())
