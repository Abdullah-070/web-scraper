# Facebook Scraper


## Input

| field | required |
|---|---|
| `business_page` | yes — a Facebook Page URL or handle (e.g. `brightsmiledental` or a full `https://facebook.com/...` URL) |

No auth needed — scrapes a public Page's "About" section, not a logged-in feed.

## Output

One row (single-element `results[]`): `contact_info`, `website`, `phone`.

## Extraction approach (post-launch fix)

Live testing found **every field coming back null**. Root cause: the
original version used guessed CSS selectors (`data-testid="..."`,
specific class names) that don't match Facebook's real markup, which
uses non-deterministic/hashed class names — there's no fixed selector
that reliably survives Facebook's build process.

Fixed by switching to signals that don't depend on CSS at all:
- **`contact_info`**: read from the `og:description` meta tag, which
  Facebook populates server-side in the raw page source regardless of
  markup/JS state.
- **`phone`**: checks for an explicit `tel:` link first; if none, falls
  back to regex-scanning the meta description/page text (same pattern as
  the Website scraper).
- **`website`**: the first external `<a>` link on the page that isn't one
  of Facebook's own domains (`facebook.com`, `fbcdn.net`, etc.).

## Anti-scraping measures (NFR-3.2)

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
- `contact_info` is whatever Facebook put in the Page's `og:description`
  summary — it's a reasonable proxy for "about" info, but isn't
  guaranteed to include every field (address, hours, etc.) a full About
  tab might show.
