# Google Maps Scraper


## Inputs

| field | required |
|---|---|
| `business_type` | yes |
| `city` | yes |
| `country` | yes |
| `max_results` | no — defaults to `DEFAULT_MAX_RESULTS` (15), configurable via `GOOGLE_MAPS_DEFAULT_MAX_RESULTS` env var |

No auth needed — Google Maps search results are public.

## Outputs

Each row in `results[]`: `business_name`, `phone`, `email`, `website`,
`address`, `rating`, `reviews`.

- `email` is always `null` — Google Maps listings don't expose email
  directly, even in the detail panel. Use the **Website Scraper** on the
  returned `website` field to get emails.
- `rating`/`reviews` are parsed from the listing's aria-label (e.g.
  `"4.5 stars 123 Reviews"` → `rating=4.5, reviews=123`).

## Post-launch fixes (from live testing feedback)

Two real bugs were found once this was tested against live Google Maps:

1. **Inconsistent result counts.** There was no cap on how many results
   were returned, so the count varied run-to-run based on how much the
   feed happened to scroll-load. Fixed via the new `max_results` input —
   output is now capped deterministically regardless of feed timing.
2. **Phone was always `null`.** Google Maps only exposes a listing's
   phone number in its **detail panel**, which only appears after
   clicking that listing — never on the list/feed card itself. The old
   code checked for a phone button on the list card, which structurally
   can never be there. The live scraper (`_scrape_live` in `scraper.py`)
   now clicks into each result (up to `max_results`) to read its phone
   number from the opened panel before moving to the next one, which
   means live scraping is slower than before but actually returns phone
   numbers now.

## Handling Google Maps' scroll-loaded results (NFR-2.2)

Google Maps loads listings via infinite scroll inside a results panel,
not standard pagination. The live scraper scrolls until either
`max_results` cards have loaded or `MAX_SCROLL_ITERATIONS` (default 6,
env-configurable) is hit, whichever comes first.

## Testing

Fixture-based tests (`tests/fixtures/google_maps_sample.html`) cover the
list-parsing path (name/rating/address/website) and `max_results`
capping. The click-through phone extraction is live-browser-only
behavior (it requires real Playwright page interaction, not static HTML)
and is documented/reasoned in code rather than fixture-tested.

```bash
pytest tests/test_google_maps_scraper.py -v
```

## Known limitations

- Clicking every result for its phone number is slower than a pure list
  scrape — for large `max_results` values, expect longer job runtimes.
- Rating/review parsing depends on Google's current aria-label format;
  if Google changes this, only `_parse_rating_label()` needs updating.
