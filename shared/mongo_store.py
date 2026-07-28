"""
MongoDB persistence layer (per Intern 2's architecture decision).

ASSUMPTIONS
- Database name: "sdip"
- Jobs collection is keyed by Mongo's own `_id` (an ObjectId). The `jobId`
  string arriving in the Redis payload is that _id's string form -- we
  convert it to ObjectId at the boundary (see `_to_object_id` below) and
  never touch the Jobs collection with a raw string.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from pymongo import MongoClient

from shared.exceptions import InvalidInputError

load_dotenv()  # reads .env in the project root -- this is where you set MONGO_URI

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB_NAME", "sdip")  # ASSUMPTION -- confirm with Intern 2

JOBS_COLLECTION = "jobs"
RESULTS_COLLECTION = "results"  # one document per scraped row: {jobId, userId, scraperType, data}

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_db():
    return get_client()[DB_NAME]


def _to_object_id(raw_id: str, field_name: str = "jobId") -> ObjectId:
    """Convert a string id from the Redis payload into a real ObjectId.
    """
    try:
        return ObjectId(raw_id)
    except (InvalidId, TypeError) as exc:
        raise InvalidInputError(
            f"'{field_name}' is not a valid MongoDB ObjectId: {raw_id!r}",
            details={"field": field_name, "value": raw_id},
        ) from exc


def get_job(job_id: str) -> dict[str, Any] | None:
    """Fetch the job document by its Mongo _id (ObjectId)."""
    db = get_db()
    return db[JOBS_COLLECTION].find_one({"_id": _to_object_id(job_id)})


def set_job_status(job_id: str, status: str, extra: dict[str, Any] | None = None) -> None:
    """Update a job's status in the Jobs collection, keyed by ObjectId _id.
    """
    db = get_db()
    update = {"status": status, "updated_at": datetime.now(timezone.utc)}
    if extra:
        update.update(extra)

    db[JOBS_COLLECTION].update_one(
        {"_id": _to_object_id(job_id)},
        {"$set": update},
    )


def save_results(
    job_id: str,
    scraper_type: str,
    rows: list[dict[str, Any]],
) -> None:
    """Insert ONE document per scraped row into the Results collection
    """
    if not rows:
        return

    job_object_id = _to_object_id(job_id)
    job_doc = get_job(job_id)
    user_id = job_doc.get("userId") if job_doc else None

    db = get_db()
    now = datetime.now(timezone.utc)

    documents = [
        {
            "jobId": job_object_id,
            "userId": user_id,  # already an ObjectId as stored on the job doc
            "scraperType": scraper_type,
            "data": row,
            "saved_at": now,
        }
        for row in rows
    ]

    db[RESULTS_COLLECTION].insert_many(documents)