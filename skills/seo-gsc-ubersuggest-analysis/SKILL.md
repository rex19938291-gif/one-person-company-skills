---
name: seo-gsc-ubersuggest-analysis
description: "Run a GSC-first SEO research and Traditional Chinese long-form content workflow using direct Google Search Console data, local GSC exports, Ubersuggest SERP and keyword context, verified sources, article-quality checks, and a required humanized Taiwan Traditional Chinese final pass. Use when 你 asks for keyword research, search-intent analysis, content gaps, SEO titles or outlines, WordPress-ready SEO articles, A/B/C article drafting, or reusable SEO writer handoffs. Use the separate seo-performance-strategy-report skill only for client-facing performance reports and HTML delivery."
---

# SEO GSC + Ubersuggest Research and Longform Content

## Purpose

Use one traceable workflow from SEO evidence to a publishable Traditional Chinese article draft:

`GSC actual performance → Ubersuggest/SERP keyword context → intent and keyword brief → article structure → fact-checked draft → humanized Taiwan Traditional Chinese pass → SEO and delivery review`

Keep source labels strict. Google Search Console is first-party actual performance. Ubersuggest is external SERP, keyword, intent, and estimate context. Never present an estimate as actual traffic or a ranking guarantee.

## Source Priority and Boundaries

1. Direct Google Search Console API with `https://www.googleapis.com/auth/webmasters.readonly`.
2. Existing local GSC/OpenSEO JSON snapshots when direct GSC access is unavailable or not authorized.
3. Ubersuggest MCP for SERP positions, keyword ideas, search difficulty/intent, competitor pages, and AI Overview presence.
4. Other tools only after 你 explicitly approves new installs, OAuth, paid queries, or browser login.

Never use Ubersuggest to replace GSC clicks, impressions, CTR, or average position. An AI Overview block does not prove that a target was cited; citation proof requires a returned source URL.

## Safety Gates

Before direct GSC work, confirm the target domain, exact property (prefer `sc-domain:<domain>`), date and comparison windows, and whether OAuth/token use is allowed. Ask for narrow, time-boxed approval before OAuth/browser sign-in, reading tokens or secrets, installing API dependencies, querying another property, or running paid queries.

Use this approval template for a direct GSC read:

```text
我同意本次限時授權：允許 Codex 在接下來 10 分鐘內使用 Google Search Console API 的唯讀 scope（webmasters.readonly）查詢 <GSC_PROPERTY>，只可讀取該 property 的 SEO performance / URL inspection 相關資料；不得讀取其他網站、不得修改網站、不得部署、不得產生付費查詢或安裝套件，除非再次向我確認。
```

If package installation is also approved, add:

```text
並允許安裝或使用本機缺少的 Python Google API 唯讀查詢依賴。
```

Do not deploy, publish, upload client data, edit a website, or trigger a paid query as part of this Skill without separate explicit approval.

## End-to-End Workflow

### 1. Orient and collect the brief

Identify the target website, GSC property if any, market/language, date window, article goal, topic, target reader, core keyword, and requested output. For a commercial or transactional article also collect the product/service facts, supported advantages, price or plan data, and CTA. Use [references/article-production.md](references/article-production.md) for the complete intake contract.

State scope and non-scope. If no approved GSC property exists, use Ubersuggest and official sources for planning but clearly label the result as external research rather than actual site performance.

### 2. Fetch or load GSC evidence

Preferred direct API path:

- Use `scripts/gsc_fetch_search_analytics.py` only after approval and dependency checks.
- Query `query`, `page`, `query,page`, and `date`; add `device`, `country`, or `searchAppearance` only when needed.
- Save raw JSON locally in a dated folder.
- Verify property, date coverage, row counts, and metric totals.
- Run `scripts/summarize_gsc_api_exports.py` for reusable annual/recent/comparison/opportunity summaries.

Snapshot path:

- Use `scripts/analyze_gsc_export.py --input <folder> --domain <domain>` for an existing export.
- Call it a snapshot and state that it may be stale if no direct refresh ran.

### 3. Add Ubersuggest keyword and SERP context

Run the availability gate first: make the cheapest free `auth_status` probe. If the Ubersuggest namespace is absent, treat it as an integration/OAuth failure, not zero data. Follow [references/ubersuggest-mcp-playbook.md](references/ubersuggest-mcp-playbook.md); do not retry the same frozen desktop task.

For Taiwan keyword-level queries use exactly `language: "zh_tw"` and `locId: 2158`. Do not substitute `zh-tw`, `zh-hant`, `cht`, `tw`, or `zh` for keyword lists. If `noData: true` appears, run the same-parameter control-domain test before concluding that the target has no data.

Use Ubersuggest for keyword ideas, difficulty, intent, SERP result pages, competitor context, content ideas, and AI Overview presence. Respect free-query discipline and never refresh paid metrics without approval. Record `updated_at` for SERP snapshots and state freshness/confidence.

### 4. Build the keyword and content brief

Combine, without conflating, the following:

- GSC query/page clusters: actual queries and pages already earning visibility.
- Ubersuggest ideas: external candidate terms, estimated demand, difficulty, and intent.
- SERP inspection: visible competitors, result types, People Also Ask, related searches, and content patterns.
- Reader problem: what the searcher needs to understand, compare, solve, buy, or book.

Return a compact handoff:

```text
文章類型：A／B／C
文章主題：
核心關鍵字：
長尾關鍵字：
相關語意詞：
主要搜尋意圖：
讀者決策問題：
建議SEO標題：
建議大綱：
必答問題：
需查證資料：
不可自行推定：
CTA目標：
資料來源與日期：
```

Label keyword volume, difficulty, traffic, and AI visibility as estimates or SERP observations unless a current named source proves otherwise.

### 5. Classify the article intent

Select exactly one mode:

- **A：資訊整合型** — definition, education, process, guide, or problem solving.
- **B：商業調查型** — recommendation, comparison, ranking, fee guide, or selection advice.
- **C：交易型導向** — product, service, brand, booking, purchase, or lead conversion.

Do not force a template that conflicts with the actual SERP intent.

### 6. Check completeness before drafting

Ask for missing core information. Safe defaults are limited to secondary choices: Taiwan Traditional Chinese, professional-clear-friendly tone, second-person introduction, four to eight FAQs, and an English lowercase hyphenated slug.

Never invent product features, prices, results, reviews, testimonials, certifications, rankings, addresses, business hours, service areas, company history, or guarantees. For B and C content, unsupported commercial claims are a blocking gap, not an invitation to guess.

### 7. Plan and draft the article

Read [references/article-production.md](references/article-production.md) for the A/B/C templates, input/output contract, WordPress format, style rules, and final checklist.

Use this default structure:

1. English lowercase slug.
2. SEO title and approximately 100–150 Chinese-character meta description.
3. Reader-situation, pain-point, misconception, risk, or market-change introduction.
4. Major sections; place a short transition paragraph after every major heading before subheadings.
5. Concrete methods, examples, comparisons, limitations, or local conditions that match intent.
6. Four to eight independent FAQs near the end.
7. A factual brand/product/service CTA after FAQ.

Use the reasoning rhythm `pain point → cause/context → concrete method → caveat/risk → correct understanding → next action`. Target about 3,000 Chinese characters or more unless the brief specifies another length. Use short mobile-readable paragraphs, lists for steps, and tables for comparisons. Do not print `H1`, `H2`, or `H3` labels in the article.

Draft for meaning first. Do not add three-part symmetry, repeated contrast formulas, or slogan-like short sentences merely to create rhythm.

### 8. Verify facts and claims

Verify laws, policies, taxes, subsidies, health, finance, prices, product specifications, store information, opening hours, statistics, rankings, certifications, current people or organizations, transport, and service areas before writing them as facts.

Prefer government/regulator, official brand, original research/formal document, professional institution, edited media, then user-supplied internal material. Separate fact, estimate, assumption, and user-provided claim. Add a source date when freshness matters. Omit unverified information or list it under `查證與待補資料`.

### 9. Humanize the Traditional Chinese final draft

For every externally facing Traditional Chinese article, invoke `$humanizer-zh` after fact/claim verification and before final SEO review. Read its `references/patterns.md` and `references/taiwan-localization.md`; also read `references/protected-content.md` when the draft contains numbers, product/service claims, CTA, URLs, quotations, prices, dates, or terms.

Preserve all protected content: verified facts and source labels, core and long-tail keywords, product names, slug/title/meta, URLs, CTA wording, prices, dates, quotations, and commercial or legal terms. Do not invent stories, outcomes, sources, or claims.

Review pattern clusters rather than banning isolated phrases. Remove only decorative patterns: forced three-or-more-item parallelism, repetitive `不是⋯⋯而是⋯⋯` or `不只是⋯⋯更是⋯⋯`, `首先／其次／最後` used merely to split prose, generic AI-era openings, empty transitions, or formulaic upbeat conclusions. Keep lists, steps, and comparisons when they communicate a real process, evidence, or decision criterion. Use natural Taiwan Traditional Chinese, standard full-width punctuation, and varied sentence length.

### 10. Run the final review and hand off

Check intent, keyword placement, slug/title/meta, section transitions, FAQ/CTA, readability, factual support, risk language, commercial honesty, required humanization, protected-content fidelity, and requested length. Return unresolved evidence gaps instead of silently filling them.

If 你 asks for a client-facing performance report, use `$seo-performance-strategy-report` after the analysis is ready. Keep report HTML, noindex preview, and Cloudflare deployment gates in that separate Skill.

## Analysis Buckets for SEO Research

When analyzing a site or planning content, create relevant buckets:

- Brand, non-brand product/service, local, and informational queries.
- High-impression low-CTR opportunities.
- Positions 4–20 push opportunities.
- Winning and declining pages.
- Content gaps, title/meta/H1/FAQ/internal-link needs.
- Homepage or migration-risk queries.

For a migration, map old query/page demand to new-page copy, headings, internal links, canonical/metadata, and CTA continuity.

## Output and Evidence Notes

Report:

- Data source, property, date range, and whether data was direct or a snapshot.
- What is proven and what is not proven.
- Keyword/content brief and prioritized actions.
- Article draft metadata, structure, and CTA.
- Ubersuggest limitations and SERP snapshot date.
- Whether AI citation source URLs were returned.
- Raw/normalized local artifact paths when created.

## Scripts

- `scripts/analyze_gsc_export.py`: summarize an existing GSC/OpenSEO JSON export folder into Markdown and JSON.
- `scripts/gsc_fetch_search_analytics.py`: direct Search Console API fetch helper; requires explicit approval and Google API dependencies.
- `scripts/summarize_gsc_api_exports.py`: summarize direct GSC API export files into annual, recent, previous-period, opportunity, and change-detection JSON/Markdown.

## References

- `references/article-production.md`: article intake, A/B/C templates, output format, WordPress skeleton, evidence gates, and final checklist.
- `references/gsc-api.md`: GSC API scope, property guard, dimensions, dependencies, and token safety.
- `references/source-boundaries.md`: what GSC, Ubersuggest, and AI visibility evidence can and cannot prove.
- `references/ubersuggest-mcp-playbook.md`: availability gate, Taiwan parameters, noData disambiguation, free-query discipline, SERP freshness, and AI Overview confidence.
- `$humanizer-zh`: required final-pass rules for natural Taiwan Traditional Chinese and protected-content fidelity.

## Verification

Before the final response, confirm the GSC property/date range or snapshot status, the source labels, the Ubersuggest freshness and quota boundary, the article type and required fields, the final checklist, the humanizer pass and protected-content fidelity, and the AI citation limitation. Never claim that an article is ready to publish if required facts or approvals remain unresolved.
