"""Fetch job listings from the JSearch API (RapidAPI).

Searches for jobs matching configured criteria and filters results
by salary and remote eligibility.
"""

import logging
from datetime import datetime, timedelta, timezone

import requests

from config import (
    RAPIDAPI_KEY,
    JOB_SEARCH_QUERY,
    JOB_MIN_SALARY,
    JOB_RESULT_COUNT,
)

logger = logging.getLogger(__name__)

JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"


def _is_within_date_range(posted_at_str, max_days=7):
    """Check if a job was posted within the last *max_days* days."""
    if not posted_at_str:
        return False
    try:
        posted_dt = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00"))
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
        return posted_dt >= cutoff
    except (ValueError, TypeError):
        return False


def _meets_salary_requirement(job, min_salary):
    """Return True if the job's listed salary meets the minimum threshold."""
    max_sal = job.get("job_max_salary")
    min_sal = job.get("job_min_salary")

    # Normalize to annual salary
    period = (job.get("job_salary_period") or "").upper()
    multiplier = 1
    if period == "HOUR":
        multiplier = 2080  # 40 hrs/wk * 52 wks
    elif period == "MONTH":
        multiplier = 12

    if max_sal is not None:
        if max_sal * multiplier >= min_salary:
            return True
    if min_sal is not None:
        if min_sal * multiplier >= min_salary:
            return True

    # If no salary data is available, include the job anyway
    return True


def _format_salary(job):
    """Build a human-readable salary string."""
    min_sal = job.get("job_min_salary")
    max_sal = job.get("job_max_salary")
    period = (job.get("job_salary_period") or "").capitalize()

    if min_sal and max_sal:
        return f"${min_sal:,.0f} - ${max_sal:,.0f} / {period}"
    if min_sal:
        return f"From ${min_sal:,.0f} / {period}"
    if max_sal:
        return f"Up to ${max_sal:,.0f} / {period}"
    return "Salary not listed"


def fetch_jobs():
    """Fetch and filter job listings.

    Returns:
        list[dict]: Up to JOB_RESULT_COUNT jobs, each with keys:
            title, company, location, salary, apply_link, posted_date,
            description_snippet
    """
    if not RAPIDAPI_KEY:
        logger.error("RAPIDAPI_KEY is not set. Cannot fetch jobs.")
        return []

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    params = {
        "query": f"{JOB_SEARCH_QUERY} remote in United States",
        "page": "1",
        "num_pages": "5",
        "date_posted": "week",
        "remote_jobs_only": "true",
        "country": "us",
    }

    try:
        logger.info(f"Searching jobs: {JOB_SEARCH_QUERY}")
        resp = requests.get(JSEARCH_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error(f"JSearch API request failed: {exc}")
        return []

    raw_jobs = data.get("data") or []
    logger.info(f"JSearch returned {len(raw_jobs)} raw results")

    filtered = []
    for job in raw_jobs:
        # Must be posted in the last 7 days
        if not _is_within_date_range(job.get("job_posted_at_datetime_utc"), max_days=7):
            continue

        # Must meet salary requirement (jobs with no salary listed are included)
        if not _meets_salary_requirement(job, JOB_MIN_SALARY):
            continue

        # Format posted date
        posted_at = job.get("job_posted_at_datetime_utc", "")
        try:
            posted_dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
            friendly_date = posted_dt.strftime("%b %d, %Y")
        except (ValueError, TypeError):
            friendly_date = "Recently"

        # Build a short description snippet
        desc = job.get("job_description") or ""
        snippet = desc[:300].rsplit(" ", 1)[0] + "..." if len(desc) > 300 else desc

        filtered.append({
            "title": job.get("job_title", "Senior Financial Analyst"),
            "company": job.get("employer_name", "Unknown Company"),
            "location": "Remote (US)",
            "salary": _format_salary(job),
            "apply_link": job.get("job_apply_link", ""),
            "posted_date": friendly_date,
            "description_snippet": snippet,
            "employer_logo": job.get("employer_logo"),
        })

        if len(filtered) >= JOB_RESULT_COUNT:
            break

    logger.info(f"Returning {len(filtered)} jobs after filtering")
    return filtered
