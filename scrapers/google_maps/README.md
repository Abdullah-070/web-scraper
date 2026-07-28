# Google Maps Scraper

Implements `FR-2.1` (Google Maps scraper module).

## Inputs

| field | required |
|---|---|
| `business_type` | yes |
| `city` | yes |
| `country` | yes |

No auth needed — Google Maps search results are public.

## Outputs

Each row in `results[]`: `business_name`, `phone`, `email`, `website`,
`address`, `rating`, `reviews`.

- `email` is always `null` — Google Maps listings don't expose email
  directly. Use the **Website Scraper** on the returned `website` field
  to get emails.
- `rating`/`reviews` are parsed from the listing's aria-label (e.g.
  `"4.5 stars 123 Reviews"` → `rating=4.5, reviews=123`).

## Handling Google Maps' scroll-loaded results (NFR-2.2)

Google Maps loads listings via infinite scroll inside a results panel,
not standard pagination. The live scraper scrolls the panel a bounded
number of times (`MAX_SCROLL_ITERATIONS` in `config.py`, default 6) with
randomized delays between scrolls, then parses whatever has loaded.
Increase this constant if you need more results per job, at the cost of
longer job runtime.

## Testing

All tests run against `tests/fixtures/google_maps_sample.html` via the
`fixture_html` param — no live browser/network needed.

```bash
pytest tests/test_google_maps_scraper.py -v
```

## Known limitations (Week 2)

- Only scrolls a bounded number of times — very large result sets will be
  truncated. Tune `MAX_SCROLL_ITERATIONS` as needed.
- Rating/review parsing depends on Google's current aria-label format;
  if Google changes this, only `_parse_rating_label()` needs updating.
