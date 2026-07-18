"""
Shared output schema for every SDIP scraper 
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_result(
    scraper_type: str,
    status: str,
    source_query: dict[str, Any],
    results: list[dict[str, Any]] | None = None,
    errors: list[dict[str, Any]] | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Build a standardized scraper output envelope.

    """
    results = results or []
    errors = errors or []

    return {
        "job_id": job_id or str(uuid.uuid4()),
        "scraper_type": scraper_type,
        "status": status,
        "scraped_at": now_iso(),
        "source_query": source_query,
        "results": results,
        "result_count": len(results),
        "errors": errors,
    }



RESULT_FIELDS = {
    "linkedin": ["name", "company", "position", "profile_url", "email", "website"],
    "google_maps": [
        "business_name",
        "phone",
        "email",
        "website",
        "address",
        "rating",
        "reviews",
    ],
    "website": ["emails", "phone_numbers", "social_links", "technologies_used"],
    "facebook": ["contact_info", "website", "phone"],
    "instagram": ["followers", "bio", "website", "email"],
}


def empty_row(scraper_type: str) -> dict[str, Any]:
    
    if scraper_type not in RESULT_FIELDS:
        raise ValueError(f"Unknown scraper_type: {scraper_type}")
    return {field: None for field in RESULT_FIELDS[scraper_type]}
