# Instagram Scraper

## Input

| field | required |
|---|---|
| `username` | yes — with or without a leading `@` (stripped automatically) |

No auth needed — scrapes a public profile page.

## Output

One row (single-element `results[]`): `followers`, `bio`, `website`, `email`.

- `email` is extracted from the bio text if present (Instagram doesn't
  expose a separate email field on public profiles), using the same
  shared regex the Website scraper uses (`shared/text_patterns.py`) —
  not duplicated logic.

## Anti-scraping measures 

Same Week 3 toolkit as Facebook, given Instagram's expected aggressive
anti-scraping:

- **Shared proxy pool** — routes through a rotating proxy if configured.
- **Shared CAPTCHA/challenge detection** — checks Instagram-specific
  selectors (`#slfErrorAlert`, `.challenge-page`) plus generic block
  keywords.
- **Retry with backoff** for transient network failures.
- **Randomized human-like delays**.

## Testing

All tests run against `tests/fixtures/instagram_profile_sample.html` —
no live browser/network needed.

```bash
pytest tests/test_instagram_scraper.py -v
```

## Known limitations (Week 3)

- Follower count and bio are parsed from public meta tags
  (`og:description`, `meta[name="description"]`) rather than Instagram's
  internal JSON data blob — simpler and more stable against markup
  changes, but may be less precise than parsing the JSON directly for
  very large accounts (Instagram sometimes rounds follower counts in
  the meta description, e.g. "1.2M" instead of an exact number).
- Only the profile's public-facing bio/meta info is scraped — no login,
  no private account access, no post-level data.
