"""
Raw Redis queue worker (replaces the earlier Celery-based approach
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal

import redis
from dotenv import load_dotenv

from shared.exceptions import ScraperError
from shared.mongo_store import save_results, set_job_status

load_dotenv()  # reads .env in the project root -- this is where you set REDIS_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sdip.workers.redis_worker")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
QUEUE_KEY = os.environ.get("SCRAPE_QUEUE_KEY", "job_queue")  # CONFIRMED with Intern 2
BRPOP_TIMEOUT_SECONDS = 5  # so the loop can check for shutdown periodically


def _get_scraper_registry():
    
    from scrapers.facebook.scraper import FacebookScraper
    from scrapers.google_maps.scraper import GoogleMapsScraper
    from scrapers.instagram.scraper import InstagramScraper
    from scrapers.linkedin.scraper import LinkedInScraper
    from scrapers.website.scraper import WebsiteScraper

    return {
        "linkedin": LinkedInScraper,
        "google_maps": GoogleMapsScraper,  # Week 2
        "website": WebsiteScraper,  # Week 2
        "facebook": FacebookScraper,  # Week 3
        "instagram": InstagramScraper,  # Week 3
    }


class RedisWorker:
    """Watches a Redis list for scrape jobs and runs them.

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

    """
    job_id = payload.get("jobId")
    scraper_type = payload.get("scraperType")
    input_params = payload.get("inputParams", {})

    if not job_id or not scraper_type:
        logger.error("Malformed job payload, missing jobId/scraperType: %s", payload)
        return {"status": "failed", "error": "malformed_payload"}

    logger.info("Picked up job %s (scraperType=%s)", job_id, scraper_type)

    try:
        set_job_status(job_id, "running")
    except ScraperError as exc:
        # e.g. jobId isn't a valid ObjectId -- can't proceed at all.
        logger.error("Could not mark job %s as running: %s", job_id, exc)
        return {"status": "failed", "errors": [exc.to_dict()]}

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

    try:
        
        save_results(job_id, scraper_type, result.get("results", []))
    except ScraperError as exc:
        logger.error("Failed to save results for job %s: %s", job_id, exc)
        result = {**result, "status": "failed", "errors": result.get("errors", []) + [exc.to_dict()]}

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
