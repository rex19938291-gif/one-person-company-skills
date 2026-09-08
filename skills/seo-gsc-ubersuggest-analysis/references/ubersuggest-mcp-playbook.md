# Ubersuggest MCP Playbook (verified end-to-end 2026-07-17)

Operational knowledge verified by a successful full run (Claude session,
行銷團隊marketing.com Taiwan analysis). Follow this exactly; every rule below
was learned from a real failure or a real success, not from documentation.

## 0. Availability Gate (run FIRST, machine-checkable)

1. Confirm at least one Ubersuggest MCP tool is callable in THIS session
 (cheapest probe: `auth_status` — free, no data query).
2. If the Ubersuggest namespace is absent from the supplied tool list:
 - This is an integration/OAuth failure, NOT zero data. Stop the SEO task.
 - Do NOT retry inside the same desktop task: the MCP tool list is frozen
 at task creation and can never hot-add a server. Only a genuinely new
 task can see a repaired connection.
 - Hand off to `<你的本機路徑>`
 (root-cause diagnosis + ordered next steps live there).
 - An empty keyword array or empty tool list without a completed tool call
 is invalid evidence for any SEO conclusion. Never report "no volume" or
 "no AI Overview" from it.

## 1. Free-Query Discipline

- Call `auth_status` first and note the tier.
- `serp_analysis` responses echo
 `limits.monthly_keyword_metrics_updates_used`. It must stay unchanged
 across your calls; cached snapshots (`"newData": false`) cost nothing.
- Never trigger a SERP/metrics refresh, `searchType: "paid"`, or any action a
 tool marks as costing credits without 你的 explicit approval.
- Reading cached data across many keywords is free — batch freely.

## 2. Language / Location Cookbook (the #1 failure source)

- Taiwan keyword database: `language: "zh_tw"` + `locId: 2158`. Both parts
 required for all keyword-level endpoints (`domain_keywords`,
 `serp_analysis`, `keyword_overview`, `page_keywords`).
- Rejected with HTTP 400: `zh-tw`, `zh-hant`, `cht`, `tw`.
- Trap: `zh` + 2158 is ACCEPTED but is the wrong bucket — it can return
 `{"noData": true}` for domains that DO have `zh_tw` data. `domain_overview`
 tolerates `zh`; keyword lists do not.
- Ubersuggest project configs confirm the canonical pair: `lang: "zh_tw"`,
 `loc_id: 2158`.

### Disambiguating `{"noData": true}`

`noData` can mean either "domain has no keywords" or "wrong language/locId
combo". Always disambiguate with a control domain on the SAME combo (e.g.
`shopee.tw` for Taiwan):

- Control returns data, target returns noData → target truly has no data.
- Control also returns noData → the combo is wrong; fix parameters before
 concluding anything.

## 3. Reading SERP Snapshots and AI Overview

- `serp_analysis` returns a cached snapshot; ALWAYS report its `updated_at`.
- Non-organic SERP features appear as their own entries (`type`:
 `people_also_ask`, `video`, `related_searches`, ...). An AI Overview, when
 present, appears the same way.
- Confidence rules:
 - Fresh snapshot (recent `updated_at`), no AI Overview entry → "no AI
 Overview" at medium-high confidence.
 - Stale snapshot (older than ~6 months, or predating AI Overview rollout
 for that language), no AI Overview entry → LOW confidence; say so
 explicitly instead of claiming absence.
- Citation proof standard is unchanged (`source-boundaries.md`): only a
 returned source URL under an AI Overview block proves citation. AI Overview
 presence alone proves nothing about the target.
- Cross-check: the position in `domain_keywords` should roughly match the
 target's position in a fresh `serp_analysis` snapshot. Large mismatch →
 one side is stale; prefer the fresher `updated_at`.

## 4. Minimal Verified Sequence — "domain TW organic + AI Overview" job

1. `auth_status` — gate + tier.
2. `domain_overview(domain, zh, 2158)` — headline counts + monthly history
 (detects collapse/growth trends worth reporting).
3. `domain_keywords(domain, zh_tw, 2158, organic)` — the actual keyword list.
 If noData, run the control-domain test before concluding.
4. `serp_analysis(keyword, zh_tw, 2158)` per keyword — record `updated_at`,
 feature entries, target position, AI Overview presence/citation.
5. Report: keywords table (position/volume/URL), per-keyword AI Overview
 verdict WITH snapshot date and confidence, citation-proof statement,
 quota-untouched statement.

## 5. Known Environment State (2026-07-17, evening update)

- Claude's Ubersuggest MCP connection works (URL-only config, this playbook
 was proven through it).
- Codex's connection is REPAIRED and end-to-end verified (2026-07-17 20:21):
 a fresh headless `codex exec` process exposed the tools, `auth_status`
 returned tier1, and a free `keyword_overview` zh_tw/2158 query returned
 real data. Repair history: `ubersuggest-mcp-oauth-repair.md` task card.
- Standing cautions that keep it working:
 - Desktop tasks created BEFORE a repair/login have frozen tool snapshots
 and will never show the namespace — always use a new task after any
 MCP/auth change.
 - Verify with ONE fresh process at a time; batched checks race the
 rotating refresh token and can kill the session.
 - After any Homebrew codex upgrade, expect one re-login before the first
 Ubersuggest use.
