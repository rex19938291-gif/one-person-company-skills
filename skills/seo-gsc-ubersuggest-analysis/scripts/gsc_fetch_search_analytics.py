#!/usr/bin/env python3
"""Fetch Google Search Console Search Analytics rows.

Do not run this script until the user has approved OAuth/token use for the
specific property. Dependencies are intentionally not vendored.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def import_google_deps():
 try:
 from google.oauth2.credentials import Credentials
 from google_auth_oauthlib.flow import InstalledAppFlow
 from google.auth.transport.requests import Request
 from googleapiclient.discovery import build
 except Exception as exc: # pragma: no cover - dependency guard
 raise SystemExit(
 "Missing Google API dependencies. Ask你before installing: "
 "google-auth google-auth-oauthlib google-api-python-client"
 ) from exc
 return Credentials, InstalledAppFlow, Request, build


def load_credentials(client_secret: Path, token_path: Path):
 Credentials, InstalledAppFlow, Request, _build = import_google_deps()
 creds = None
 if token_path.exists():
 creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
 if creds and creds.expired and creds.refresh_token:
 creds.refresh(Request())
 if not creds or not creds.valid:
 flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
 creds = flow.run_local_server(port=0)
 token_path.parent.mkdir(parents=True, exist_ok=True)
 token_path.write_text(creds.to_json(), encoding="utf-8")
 return creds


def fetch(service: Any, site_url: str, start_date: str, end_date: str, dimensions: list[str], row_limit: int):
 body = {
 "startDate": start_date,
 "endDate": end_date,
 "dimensions": dimensions,
 "rowLimit": row_limit,
 }
 return service.searchanalytics().query(siteUrl=site_url, body=body).execute()


def main() -> int:
 parser = argparse.ArgumentParser()
 parser.add_argument("--site-url", required=True, help="Exact GSC property, e.g. sc-domain:example.com")
 parser.add_argument("--allowed-site-url", required=True, help="Safety guard; must equal --site-url")
 parser.add_argument("--start-date", required=True)
 parser.add_argument("--end-date", required=True)
 parser.add_argument("--dimensions", required=True, help="Comma-separated dimensions")
 parser.add_argument("--row-limit", type=int, default=25000)
 parser.add_argument("--client-secret", required=True, help="OAuth client secret JSON path")
 parser.add_argument("--token", required=True, help="Task-specific token JSON path")
 parser.add_argument("--out", required=True, help="Output JSON path")
 args = parser.parse_args()

 if args.site_url != args.allowed_site_url:
 raise SystemExit("Refusing to query a GSC property outside the approved property.")

 client_secret = Path(args.client_secret).expanduser().resolve()
 token_path = Path(args.token).expanduser().resolve()
 out_path = Path(args.out).expanduser().resolve()
 dimensions = [item.strip() for item in args.dimensions.split(",") if item.strip()]
 if not dimensions:
 raise SystemExit("At least one dimension is required.")

 creds = load_credentials(client_secret, token_path)
 _Credentials, _InstalledAppFlow, _Request, build = import_google_deps()
 service = build("searchconsole", "v1", credentials=creds)
 result = fetch(service, args.site_url, args.start_date, args.end_date, dimensions, args.row_limit)

 out_path.parent.mkdir(parents=True, exist_ok=True)
 out_path.write_text(
 json.dumps(
 {
 "siteUrl": args.site_url,
 "startDate": args.start_date,
 "endDate": args.end_date,
 "dimensions": dimensions,
 "rowLimit": args.row_limit,
 "result": result,
 },
 ensure_ascii=False,
 indent=2,
 ),
 encoding="utf-8",
 )
 print(json.dumps({"output": str(out_path), "rows": len(result.get("rows", []))}, ensure_ascii=False))
 return 0


if __name__ == "__main__":
 raise SystemExit(main())
