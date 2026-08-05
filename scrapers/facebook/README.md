# Facebook Scraper

## Input

| field | required |
|---|---|
| `business_page` | yes — a Facebook Page URL or handle (e.g. `brightsmiledental` or a full `https://facebook.com/...` URL) |

No auth needed — scrapes a public Page's "About" section, not a logged-in feed.

## Output

One row (single-element `results[]`): `contact_info`, `website`, `phone`.

## Anti-scraping measures 

Facebook is expected to apply more aggressive anti-scraping than Google
Maps/Website, so this scraper uses the full Week 3 toolkit from the start:

- **Shared proxy pool** (`shared/proxy_pool.py`) — routes requests through
  a rotating proxy if `PROXY_LIST` is configured; no-op otherwise.
- **Shared CAPTCHA/checkpoint detection** (`shared/captcha_detection.py`)
  — checks both Facebook-specific selectors (`#checkpointSubmitButton`,
  `.captcha_body`) and generic block-page keywords.
- **Retry with backoff** (`shared/retry.py`) — retries transient network
  failures up to 3 times.
- **Randomized human-like delays** between navigation actions.

## Testing

All tests run against `tests/fixtures/facebook_page_sample.html` — no
live browser/network needed.

```bash
pytest tests/test_facebook_scraper.py -v
```

## Known limitations 

- Only scrapes the Page's "About" tab — doesn't crawl posts, reviews, or
  other tabs.
- Selector-based parsing depends on Facebook's current markup; if it
  changes, only `scrapers/facebook/config.py` needs updating.
