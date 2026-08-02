# SDIP Scraper Engine — Shared API Contract (v2, Week 1)


## 1. Queue architecture: raw Redis (not Celery/RQ, not BullMQ)

Backend uses Node + BullMQ conventions on his side; this engine is
Python. BullMQ and Celery/RQ each serialize queue data into Redis using
their own framework-specific format — a Celery worker cannot read a
BullMQ-pushed job, and vice versa. To avoid this, **both sides talk to
Redis directly with plain client libraries**, pushing/reading plain JSON,
no queue framework in between.

- Backend (Node): `ioredis` or `redis` — pushes JSON via `LPUSH`
- Scraper (Python): `redis-py` — reads JSON via `BRPOP`
- Queue key: **`job_queue`**

## 2. End-to-end flow

1. User creates a job from the frontend → hits Backend's API
2. Backend saves the job in MongoDB (`jobs` collection) with `status: "pending"`
3. Backend pushes a JSON payload onto the Redis list:
   ```json
   { "jobId": "string", "scraperType": "linkedin", "inputParams": { ... } }
   ```
4. Scraper's worker (`workers/redis_worker.py`) `BRPOP`s that same list
5. On pickup, the worker sets `status: "running"` in MongoDB
6. The worker runs the matching scraper (see Section 4 for envelope shape)
7. The worker saves the result to the `results` collection and sets the
   job's status to `"completed"` or `"failed"`

## 3. MongoDB contract

**DB name is now CONFIRMED via a MongoDB Compass screenshot (cluster
`cluster0.fhklglk.mongodb.net` → database `sdip` → collections `jobs`,
`results`, `users`). Everything below is confirmed except where noted.**

| | value | status |
|---|---|---|
| DB name | `sdip` | **confirmed** (seen directly in Compass) |
| Jobs collection | `jobs`, keyed by Mongo's own `_id` (ObjectId) | **confirmed** |
| Results collection | `results` | confirmed |
| Users collection | `users` — exists, but this scraper engine never reads/writes it directly; `userId` on a job doc is a foreign key into it | **confirmed exists** (not previously known) |
| Result document | ONE PER SCRAPED ROW: `{ jobId, userId, scraperType, data }` | **confirmed** |
| jobId / userId type | always `ObjectId`, never a plain string | **confirmed** |
| Job status values | `"pending"` \| `"running"` \| `"completed"` \| `"failed"` | **confirmed** |

**Job document shape, as observed directly in Compass** (Backend's side
writes this; our worker only updates `status`/`updatedAt` on it):
```json
{
  "_id": ObjectId("..."),
  "userId": ObjectId("..."),
  "scraperType": "linkedin",
  "inputParams": { /* the scraper's input fields */ },
  "status": "pending",
  "createdAt": ISODate("..."),
  "updatedAt": ISODate("..."),
  "__v": 0
}
```
The `createdAt`/`updatedAt`/`__v` fields indicate Backend's Node side
uses **Mongoose** (an ODM) to create job docs — worth knowing if a schema
mismatch ever comes up, since Mongoose enforces its own schema on writes
from his side, independent of whatever pymongo does on ours.
`shared/mongo_store.py::set_job_status()` intentionally only ever writes
`status` and its own `updated_at` field, so it doesn't fight with
Mongoose's schema or accidentally strip fields Backend's side relies on.

Notes on the confirmed Result schema:
- **One document is inserted per scraped row**, not one document for the
  whole job. E.g. a Google Maps search returning 10 dentists in Islamabad
  produces 10 separate Results documents, each with its own `data` object
  holding that single listing's fields — not one document containing an
  array of 10.
- `data` holds a single row's scraped fields (the shape from
  `shared/schema.py::RESULT_FIELDS` for that scraper type) — NOT the
  whole standardized output envelope. The envelope's `job_id`,

  `status`, `errors`, etc. live only on the Job document / worker return
  value, not duplicated onto every result row.
- `jobId` and `userId` are stored as real Mongo `ObjectId`s, converted at
  the boundary in `shared/mongo_store.py::_to_object_id()`. The Redis
  payload's `jobId` arrives as a string (JSON has no ObjectId type) and
  is converted immediately before touching MongoDB — string ids are
  never written to either collection.
- `userId` is **not** included in the Redis job payload (Section 2) — the
  worker looks it up from the job's own document in the Jobs collection
  (`shared/mongo_store.py::get_job()`) before saving results. This means
  the Jobs collection must have `userId` set on the job doc (as an
  ObjectId) before the worker picks up the corresponding queue message.

Scraper connects directly via `pymongo` (no API call back to Backend's
Node server) — per his instruction. Job status writes: `running`,
`completed`, `failed`. `pending` is set by Backend's side only.

## 4. Auth contract (LinkedIn, Week 1)

```json
{
  "auth": {
    "account_id": "string — identifies which connected account this is, for rate limiting",
    "session_cookie": "string — the user's li_at session cookie value"
  }
}
```

- The scraper never stores this. It's used only for the duration of one
  job run.
- Credential storage/encryption/refresh is entirely the backend's
  responsibility (likely via Settings > API Keys pattern, Sec 2.7 of the
  source doc).
- `account_id` is required even before real backend integration — it's
  what the daily rate limiter keys off of (FR-1.9). Jobs without it are
  rejected with `invalid_input` rather than silently falling back to a
  shared bucket, since that would defeat per-account rate limiting.

## 5. Output envelope (all scrapers, FR-1.6)

Every job — regardless of scraper type — returns exactly this shape:

```json
{
  "job_id": "string (uuid)",
  "scraper_type": "linkedin",
  "status": "completed | failed",
  "scraped_at": "ISO 8601 timestamp",
  "source_query": { "...scraper-specific input fields, auth/session data stripped..." },
  "results": [ { "...scraper-specific fields, see below..." } ],
  "result_count": 0,
  "errors": [
    {
      "error_type": "invalid_input | authentication_error | rate_limit_exceeded | blocked_or_captcha | network_error | parsing_error | unhandled_exception",
      "message": "string",
      "details": {}
    }
  ]
}
```

**Important:** `source_query` never includes `auth` or any credential/session
data, and never includes internal test-only fields like `fixture_html`.
This is enforced by `BaseScraper._public_source_query()` — no scraper
should bypass it.

## 6. Per-scraper `results[]` field contract

| scraper_type  | fields (always present, `null` if not found) |
|---|---|
| `linkedin`    | `name`, `company`, `position`, `profile_url`, `email`, `website` |
| `google_maps` | `business_name`, `phone`, `email`, `website`, `address`, `rating`, `reviews` |
| `website`     | `emails`, `phone_numbers`, `social_links`, `technologies_used` |
| `facebook`    | `contact_info`, `website`, `phone` |
| `instagram`   | `followers`, `bio`, `website`, `email` |

Every key must be present on every row — use `null`, never omit a key.
Source of truth: `shared/schema.py::RESULT_FIELDS`.

## 7. Job status mapping (Sec 2.4 of source doc)

The dashboard expects: `Pending`, `Running`, `Completed`, `Failed`.

- `Pending` is set by Backend when the job doc is first created in MongoDB.
- `Running`, `Completed`, `Failed` are set by Scraper's worker directly
  in MongoDB (`shared/mongo_store.py::set_job_status`), as the job is
  picked up and finishes.

## 8. Error taxonomy (`error_type` values)

Defined in `shared/exceptions.py`. Used consistently across all scrapers
so the Failed Tasks dashboard view can group/filter by cause:

- `invalid_input` — bad params, caught before any scraping starts
- `authentication_error` — missing/invalid/expired session
- `rate_limit_exceeded` — daily cap hit for that account
- `blocked_or_captcha` — target site blocked us / showed a CAPTCHA
- `network_error` — timeout/connection issue (retryable)
- `parsing_error` — page loaded but expected structure wasn't found
- `unhandled_exception` — a bug; should not happen in a finished scraper

## 9. What's still a placeholder / open

- **Rate limiting** (`shared/rate_limit.py::FileRateLimiter`) still uses a
  local JSON file rather than MongoDB. Now that a real Mongo connection
  exists (`shared/mongo_store.py`), this is a natural next thing to move
  into Mongo too — flagged, not yet done.
- **PROXY_LIST** is not populated anywhere yet — proxy rotation code
  exists and is tested but currently runs in no-op mode on every real job.
- **Redis Cloud connection stability**: the shared Redis instance (Redis
  Cloud, `*.redislabs.com`) has been observed dropping idle connections
  mid-`BRPOP`, raising `ConnectionResetError` on the Python side. The
  worker now auto-reconnects (`workers/redis_worker.py::RedisWorker._connect()`,
  with `socket_keepalive=True` + reconnect-on-drop in the main loop) so
  this no longer crashes the process, but it's worth knowing the
  underlying instance does this — if drops become frequent enough to
  matter for job latency, worth revisiting with Backend (e.g. a
  paid/dedicated Redis tier, or a shorter `BRPOP` timeout with more
  frequent reconnects).