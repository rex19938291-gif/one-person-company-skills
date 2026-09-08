# GSC API Notes

Use Google Search Console API only after你gives time-boxed approval.

## Scope

Use the minimum read-only scope:

```text
https://www.googleapis.com/auth/webmasters.readonly
```

Do not request write scopes.

## Property Guard

Prefer domain properties:

```text
sc-domain:example.com
```

If你approves only one property, every request must check the `siteUrl` exactly matches that property before execution.

## Search Analytics Dimensions

Useful dimensions:

- `query`: query-level demand and CTR.
- `page`: page-level performance.
- `query,page`: page-query mapping for migration and content planning.
- `date`: trend and comparison windows.
- `device`: mobile/desktop differences.
- `country`: market focus.
- `searchAppearance`: rich result and appearance segmentation where available.

## Dependency Check

The helper script expects:

- `google-auth`
- `google-auth-oauthlib`
- `google-api-python-client`

If missing, stop and ask before installing packages.

## Google Cloud API Enablement

If the API call fails with `accessNotConfigured` or says Search Console API has not been used in the OAuth client project, the OAuth login may have succeeded but the Google Cloud project behind the client has not enabled Search Console API.

Do not enable the API automatically. Treat this as a Google Cloud configuration change and ask你first. The safe next action is enabling only:

```text
searchconsole.googleapis.com
```

for the OAuth client's Google Cloud project, then retry the same property-guarded read-only query.

## Token Handling

Tokens and client secrets are sensitive:

- Do not read existing token files without approval.
- Store any newly created token under a task-specific local path when possible.
- Redact token paths and token contents from final responses.
- Never paste token values into chat or handoffs.

## Cost

GSC API requests do not create DataForSEO/OpenSEO paid usage, but OAuth and Google account access are sensitive. Paid SERP/AI citation tools require separate approval.
