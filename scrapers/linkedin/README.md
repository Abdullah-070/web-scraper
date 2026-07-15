# LinkedIn Scraper

Implements `FR-1.3` (LinkedIn scraper module) and the Week 1 auth/rate-limit/
pacing requirements (`FR-1.8`, `FR-1.9`, `FR-1.10`).

## Inputs

| field | required | notes |
|---|---|---|
| `keywords` | yes | search term |
| `location` | yes | |
| `industry` | yes | |
| `company_size` | yes | |
| `auth.account_id` | yes | used for daily rate-limit tracking |
| `auth.session_cookie` | yes* | the end user's LinkedIn `li_at` session cookie |
| `fixture_html` | no | dev/test only — bypasses auth + live network call entirely |

\* not required when `fixture_html` is supplied (test mode).

## Outputs

Each row in `results[]`: `name`, `company`, `position`, `profile_url`,
`email`, `website` (email/website are currently always `null` — see
"Known limitations" below).

## Auth model

No LinkedIn partner API, no `linkedin-api`-style library, and **no
personal/developer account is ever used** — including for testing. The
end user connects their own LinkedIn account elsewhere in the platform;
this module only consumes the resulting session cookie for the duration
of a single job.

## Anti-ban measures (Week 1 scope)

- Randomized delays between navigation actions (`shared/human_behavior.py`)
- Daily scrape cap per connected account, default 50/day
  (`scrapers/linkedin/config.py::DEFAULT_DAILY_LIMIT`)
- CAPTCHA/challenge page detection → job fails cleanly with
  `blocked_or_captcha` rather than retrying blindly

Full proxy rotation and CAPTCHA *solving* are Week 3 scope (FR-3.3/3.4),
not built here.

## Testing

All tests run against `tests/fixtures/linkedin_search_sample.html` via the
`fixture_html` param — no live account, personal or otherwise, is ever
touched during testing.

```bash
pytest tests/test_linkedin_scraper.py -v
```

## Known limitations (Week 1)

- `email` and `website` are not extracted — LinkedIn search result cards
  don't expose them directly. Getting them would require visiting each
  profile individually, which multiplies request volume and ban risk;
  deliberately deferred rather than built into Week 1.
- Only a single search results page is scraped (no pagination yet).
- `FileRateLimiter` is a local-JSON stand-in; see `docs/api_contract.md`
  Section 7 for the real backend swap-in plan.
