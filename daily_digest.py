#!/usr/bin/env python3
"""Daily Digest - Aggregates news and sports scores into a morning email.

Usage:
    python daily_digest.py           Send the digest email
    python daily_digest.py --dry-run Build the digest and print to stdout (no email sent)
    python daily_digest.py --test    Send a short test email to verify SMTP setup
"""

import sys
import logging
from news_fetcher import fetch_all_news
from scores_fetcher import fetch_all_scores
from email_builder import build_email
from email_sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("daily_digest")


def run_digest(dry_run=False):
    """Build and send (or preview) the daily digest."""
    logger.info("Starting Daily Digest...")

    # Fetch news
    logger.info("Fetching news articles...")
    news_data = fetch_all_news()
    total_articles = sum(len(a) for a in news_data.values())
    logger.info(f"Fetched {total_articles} news articles across {len(news_data)} sections")

    # Fetch scores
    logger.info("Fetching sports scores...")
    scores_data = fetch_all_scores()
    total_games = sum(len(g) for g in scores_data.values())
    logger.info(f"Fetched {total_games} completed games across {len(scores_data)} leagues")

    # Build email
    logger.info("Building email...")
    subject, html_body = build_email(news_data, scores_data)

    if dry_run:
        print(f"\nSubject: {subject}")
        print(f"HTML Length: {len(html_body)} characters")
        print("\n--- NEWS SUMMARY ---")
        for section, articles in news_data.items():
            print(f"\n{section} ({len(articles)} articles):")
            for i, a in enumerate(articles, 1):
                print(f"  {i}. {a['title']}")
        print("\n--- SCORES SUMMARY ---")
        if scores_data:
            for league, games in scores_data.items():
                print(f"\n{league}:")
                for g in games:
                    print(f"  {g['home_team']} {g['home_score']} - {g['away_score']} {g['away_team']}")
        else:
            print("  No completed games in the past 24 hours.")
        print("\nDry run complete. No email sent.")
        return

    # Send email
    logger.info("Sending email...")
    send_email(subject, html_body)
    logger.info("Daily Digest sent successfully!")


def send_test_email():
    """Send a minimal test email to verify SMTP configuration."""
    subject = "Daily Digest - Test Email"
    html = """<html><body>
    <h2>Daily Digest Test</h2>
    <p>If you received this email, your Gmail SMTP configuration is working correctly.</p>
    <p>The daily digest will be delivered every morning at 7:00 AM.</p>
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
    run_digest(dry_run=dry_run)


if __name__ == "__main__":
    main()
