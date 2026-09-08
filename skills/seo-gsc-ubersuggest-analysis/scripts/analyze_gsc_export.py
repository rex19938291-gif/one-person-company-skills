#!/usr/bin/env python3
"""Summarize a GSC/OpenSEO JSON export folder.

Expected files are the OpenSEO-style JSON exports used in你的 workflows:
summary.mcp.json, queries.mcp.json, pages.mcp.json, query_pages.mcp.json,
dates.mcp.json, devices.mcp.json, countries.mcp.json, and report-summary.json.
Missing files are tolerated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
 with path.open("r", encoding="utf-8") as f:
 return json.load(f)


def rows_from_payload(payload: Any) -> list[dict[str, Any]]:
 if isinstance(payload, list):
 return [row for row in payload if isinstance(row, dict)]
 if isinstance(payload, dict):
 for key in ("rows", "data", "items", "results"):
 value = payload.get(key)
 if isinstance(value, list):
 return [row for row in value if isinstance(row, dict)]
 nested = payload.get("result")
 if isinstance(nested, dict):
 return rows_from_payload(nested)
 return []


def metric(row: dict[str, Any], key: str) -> float:
 value = row.get(key)
 if isinstance(value, (int, float)):
 return float(value)
 try:
 return float(value)
 except (TypeError, ValueError):
 return 0.0


def label(row: dict[str, Any]) -> str:
 keys = row.get("keys")
 if isinstance(keys, list):
 return " | ".join(str(k) for k in keys)
 for key in ("query", "page", "date", "device", "country"):
 if key in row:
 return str(row[key])
 return json.dumps(row, ensure_ascii=False)[:120]


def top_rows(rows: list[dict[str, Any]], by: str, limit: int) -> list[dict[str, Any]]:
 return sorted(rows, key=lambda row: metric(row, by), reverse=True)[:limit]


def summarize_file(folder: Path, name: str, limit: int) -> dict[str, Any]:
 path = folder / name
 if not path.exists():
 return {"file": name, "exists": False, "row_count": 0, "top": []}
 rows = rows_from_payload(load_json(path))
 return {
 "file": name,
 "exists": True,
 "row_count": len(rows),
 "top": [
 {
 "label": label(row),
 "clicks": metric(row, "clicks"),
 "impressions": metric(row, "impressions"),
 "ctr": metric(row, "ctr"),
 "position": metric(row, "position"),
 }
 for row in top_rows(rows, "clicks", limit)
 ],
 }


def write_markdown(summary: dict[str, Any], output: Path) -> None:
 lines: list[str] = []
 lines.append(f"# SEO GSC Snapshot Summary: {summary['domain']}")
 lines.append("")
 lines.append(f"- Source folder: `{summary['source_folder']}`")
 lines.append(f"- Snapshot note: {summary['snapshot_note']}")
 report = summary.get("report_summary")
 if isinstance(report, dict):
 lines.append(f"- Report summary file: available")
 for key in ("property", "startDate", "endDate", "clicks", "impressions", "ctr", "position"):
 if key in report:
 lines.append(f"- {key}: `{report[key]}`")
 lines.append("")
 for section in summary["sections"]:
 lines.append(f"## {section['file']}")
 lines.append("")
 if not section["exists"]:
 lines.append("- Missing")
 lines.append("")
 continue
 lines.append(f"- Rows: {section['row_count']}")
 lines.append("")
 lines.append("| Label | Clicks | Impressions | CTR | Avg position |")
 lines.append("|---|---:|---:|---:|---:|")
 for row in section["top"]:
 lines.append(
 f"| {row['label']} | {row['clicks']:.0f} | {row['impressions']:.0f} | {row['ctr']:.4f} | {row['position']:.2f} |"
 )
 lines.append("")
 output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
 parser = argparse.ArgumentParser()
 parser.add_argument("--input", required=True, help="GSC export folder")
 parser.add_argument("--domain", required=True, help="Target domain label")
 parser.add_argument("--out", default="", help="Output folder; defaults to input folder")
 parser.add_argument("--limit", type=int, default=20)
 args = parser.parse_args()

 folder = Path(args.input).expanduser().resolve()
 out_dir = Path(args.out).expanduser().resolve() if args.out else folder
 out_dir.mkdir(parents=True, exist_ok=True)

 sections = [
 summarize_file(folder, "queries.mcp.json", args.limit),
 summarize_file(folder, "pages.mcp.json", args.limit),
 summarize_file(folder, "query_pages.mcp.json", args.limit),
 summarize_file(folder, "dates.mcp.json", args.limit),
 summarize_file(folder, "devices.mcp.json", args.limit),
 summarize_file(folder, "countries.mcp.json", args.limit),
 ]

 report_path = folder / "report-summary.json"
 report_summary = load_json(report_path) if report_path.exists() else None
 summary = {
 "domain": args.domain,
 "source_folder": str(folder),
 "snapshot_note": "Existing export; refresh with direct GSC API before calling it current.",
 "report_summary": report_summary,
 "sections": sections,
 }

 json_out = out_dir / f"{args.domain.replace('/', '_')}-gsc-summary.json"
 md_out = out_dir / f"{args.domain.replace('/', '_')}-gsc-summary.md"
 json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
 write_markdown(summary, md_out)
 print(json.dumps({"json": str(json_out), "markdown": str(md_out)}, ensure_ascii=False))
 return 0


if __name__ == "__main__":
 raise SystemExit(main())
