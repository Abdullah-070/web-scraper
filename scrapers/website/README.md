# Website Scraper

Implements `FR-2.2` (Website scraper module).

## Input

| field | required |
|---|---|
| `website_url` | yes |

## Output

One row (single-element `results[]`): `emails`, `phone_numbers`,
`social_links`, `technologies_used`.

## Design notes

- Uses plain `requests` + BeautifulSoup, **not Playwright** — this
  scraper doesn't need JS rendering to extract contact info from most
  sites, and staying lightweight lets it run far more jobs per minute
  than the browser-based scrapers.
- No `fixture_html` bypass like LinkedIn/Google Maps — there's no
  live-account ban risk to avoid here, so tests instead monkeypatch
  `requests.get` directly.
- Technology detection (`technologies_used`) is a lightweight signature
  match (WordPress, Shopify, Wix, Squarespace, React, Google
  Analytics/Tag Manager) — not a full Wappalyzer-style detector. Extend
  `TECH_SIGNATURES` in `config.py` to add more.

## Handling bad URLs gracefully (NFR-2.1)

- Empty or malformed URLs (e.g. containing spaces, no valid domain shape)
  are rejected by `validate_input()` **before any network call is made** —
  fails with `invalid_input`, not a confusing DNS error.
- Connection errors, timeouts, and non-2xx HTTP responses are caught and
  raised as `NetworkError` (retryable, per `shared/retry.py`) rather than
  crashing the worker.

## Testing

```bash
pytest tests/test_website_scraper.py -v
```

All tests mock `requests.get` — no real network calls are made.

## Known limitations (Week 2)

- Only scrapes the given URL's landing page — doesn't crawl subpages
  (e.g. a dedicated `/contact` page) looking for more contact info.
- Technology detection is signature-based and not exhaustive.
