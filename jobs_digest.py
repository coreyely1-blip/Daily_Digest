#!/usr/bin/env python3
"""Job Alert Digest - Sends a daily email with matching job listings.

Usage:
    python jobs_digest.py           Send the job alert email
    python jobs_digest.py --dry-run Search and print results (no email sent)
    python jobs_digest.py --test    Send a short test email to verify SMTP setup
"""

import sys
import logging
from jobs_fetcher import fetch_jobs
from jobs_email_builder import build_jobs_email
from email_sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("jobs_digest")


def run_jobs_digest(dry_run=False):
    """Fetch jobs, build the email, and send (or preview) it."""
    logger.info("Starting Job Alert Digest...")

    # Fetch matching jobs
    logger.info("Searching for jobs...")
    jobs = fetch_jobs()
    logger.info(f"Found {len(jobs)} matching jobs")

    # Build email
    logger.info("Building job alert email...")
    subject, html_body = build_jobs_email(jobs)

    if dry_run:
        print(f"\nSubject: {subject}")
        print(f"HTML Length: {len(html_body)} characters")
        print(f"\n--- JOB LISTINGS ({len(jobs)} found) ---\n")
        for i, job in enumerate(jobs, 1):
            print(f"  {i}. {job['title']}")
            print(f"     Company:  {job['company']}")
            print(f"     Location: {job['location']}")
            print(f"     Salary:   {job['salary']}")
            print(f"     Posted:   {job['posted_date']}")
            print(f"     Link:     {job['apply_link']}")
            print()
        if not jobs:
            print("  No jobs matched the search criteria.")
        print("Dry run complete. No email sent.")
        return

    # Send email
    logger.info("Sending job alert email...")
    send_email(subject, html_body)
    logger.info("Job Alert email sent successfully!")


def send_test_email():
    """Send a minimal test email to verify SMTP configuration."""
    subject = "Job Alert - Test Email"
    html = """<html><body>
    <h2>Job Alert Test</h2>
    <p>If you received this email, your Gmail SMTP configuration is working correctly.</p>
    <p>The job alert digest will be delivered every morning at 10:00 AM ET.</p>
    </body></html>"""

    logger.info("Sending test email...")
    send_email(subject, html)
    logger.info("Test email sent successfully!")


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--test" in args:
        send_test_email()
        return

    dry_run = "--dry-run" in args
    run_jobs_digest(dry_run=dry_run)


if __name__ == "__main__":
    main()
