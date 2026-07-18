"""
Raw Redis queue worker (replaces the earlier Celery-based approach --
architecture decision from Intern 2, confirmed over voice message).

Why raw Redis instead of Celery/RQ: Intern 2 uses Node + BullMQ. BullMQ
and Celery/RQ each serialize queue data into Redis in their own
framework-specific format, so a Celery worker cannot read a BullMQ job
and vice versa. The fix both sides agreed on: talk to Redis directly with
plain client libraries (ioredis on his side, redis-py here), pushing and
reading plain JSON. No queue framework in between.

Flow (per Intern 2's voice message):
    1. Frontend -> his API -> Mongo job doc created, status=pending
    2. His API pushes {jobId, scraperType, inputParams} as JSON onto a
       Redis list
    3. This worker BRPOPs that same list
    4. On pickup: set status=running in Mongo
    5. Run the scraper
    6. Save result to Results collection, set status=completed/failed

ASSUMPTION (flag with Intern 2 -- not yet confirmed): the Redis list key
name is "scrape_jobs" below. If his push side uses a different key, this
is the only line that needs to change.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal

import redis

from shared.mongo_store import save_result, set_job_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sdip.workers.redis_worker")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
QUEUE_KEY = os.environ.get("SCRAPE_QUEUE_KEY", "scrape_jobs")  # ASSUMPTION -- confirm with Intern 2
BRPOP_TIMEOUT_SECONDS = 5  # so the loop can check for shutdown periodically


def _get_scraper_registry():
    # Imported lazily so this module can be imported (e.g. for testing)
    # without requiring every scraper's dependencies (Playwright, etc.)
    # to be installed.
    from scrapers.linkedin.scraper import LinkedInScraper

    return {
        "linkedin": LinkedInScraper,
        # "google_maps": GoogleMapsScraper,   # Week 2
        # "website": WebsiteScraper,           # Week 2
        # "facebook": FacebookScraper,          # Week 3
        # "instagram": InstagramScraper,        # Week 3
    }


class RedisWorker:
    """Watches a Redis list for scrape jobs and runs them.

    This class does the BRPOP loop + Mongo status bookkeeping. The actual
    scraper dispatch is delegated to `process_job`, which is what the
    tests exercise directly (without needing a live Redis connection).
    """

    def __init__(self, redis_url: str = REDIS_URL, queue_key: str = QUEUE_KEY):
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.queue_key = queue_key
        self._shutdown = False

    def request_shutdown(self, *_args) -> None:
        logger.info("Shutdown requested -- will stop after the current job.")
        self._shutdown = True

    def run_forever(self) -> None:
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)

        logger.info("Worker listening on Redis list '%s'...", self.queue_key)
        while not self._shutdown:
            item = self.redis_client.brpop(self.queue_key, timeout=BRPOP_TIMEOUT_SECONDS)
            if item is None:
                continue  # timed out waiting, loop again (lets shutdown flag be checked)

            _key, raw_payload = item
            asyncio.run(self._handle_payload(raw_payload))

    async def _handle_payload(self, raw_payload: str) -> None:
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            logger.error("Received non-JSON payload on queue, skipping: %r", raw_payload)
            return

        await process_job(payload)


async def process_job(payload: dict) -> dict:
    """Process a single job payload: {jobId, scraperType, inputParams}.

    Separated from the Redis loop so it can be unit tested directly with
    a plain dict, without needing a live Redis connection (mirrors how
    tests/test_linkedin_scraper.py tests the scraper without a live
    LinkedIn account).
    """
    job_id = payload.get("jobId")
    scraper_type = payload.get("scraperType")
    input_params = payload.get("inputParams", {})

    if not job_id or not scraper_type:
        logger.error("Malformed job payload, missing jobId/scraperType: %s", payload)
        return {"status": "failed", "error": "malformed_payload"}

    logger.info("Picked up job %s (scraperType=%s)", job_id, scraper_type)
    set_job_status(job_id, "running")

    registry = _get_scraper_registry()
    scraper_cls = registry.get(scraper_type)

    if scraper_cls is None:
        result = {
            "job_id": job_id,
            "scraper_type": scraper_type,
            "status": "failed",
            "source_query": input_params,
            "results": [],
            "result_count": 0,
            "errors": [
                {
                    "error_type": "unknown_scraper_type",
                    "message": f"No scraper registered for type '{scraper_type}'.",
                    "details": {"available": list(registry.keys())},
                }
            ],
        }
    else:
        scraper = scraper_cls(job_id=job_id)
        result = await scraper.run(input_params)

    save_result(job_id, result)
    set_job_status(job_id, result["status"])

    logger.info(
        "Job %s finished with status=%s, result_count=%s",
        job_id,
        result["status"],
        result.get("result_count", 0),
    )
    return result


if __name__ == "__main__":
    worker = RedisWorker()
    worker.run_forever()
