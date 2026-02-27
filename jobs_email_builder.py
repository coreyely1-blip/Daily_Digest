"""Build a styled HTML email for daily job alert listings."""

from datetime import datetime

import pytz

from config import TIMEZONE, JOB_SEARCH_QUERY, JOB_MIN_SALARY


def _get_formatted_date():
    """Get today's date formatted for the email subject/header."""
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    return now.strftime("%A, %B %d, %Y")


def _build_job_card_html(job, index):
    """Build HTML for a single job listing card."""
    logo_html = ""
    if job.get("employer_logo"):
        logo_html = (
            f'<img src="{job["employer_logo"]}" alt="{job["company"]}" '
            f'style="width:40px;height:40px;border-radius:6px;object-fit:contain;'
            f'margin-right:12px;border:1px solid #e0e0e0;" />'
        )

    return f"""
    <tr><td style="padding:12px 30px;">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#f8f9fa;border-radius:8px;border-left:4px solid #2563eb;
                      overflow:hidden;">
            <tr><td style="padding:16px 20px;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="vertical-align:top;width:52px;">
                            {logo_html}
                        </td>
                        <td style="vertical-align:top;">
                            <div style="font-size:16px;font-weight:bold;color:#1a1a2e;
                                        margin-bottom:4px;">
                                {index}. {job['title']}
                            </div>
                            <div style="font-size:14px;color:#4b5563;margin-bottom:6px;">
                                {job['company']}
                            </div>
                        </td>
                    </tr>
                </table>

                <table width="100%" cellpadding="0" cellspacing="0"
                       style="margin-top:8px;">
                    <tr>
                        <td style="font-size:12px;color:#6b7280;padding:2px 0;">
                            <span style="display:inline-block;background:#dbeafe;color:#1e40af;
                                         font-size:11px;padding:3px 8px;border-radius:4px;
                                         margin-right:6px;">Remote (US)</span>
                            <span style="display:inline-block;background:#dcfce7;color:#166534;
                                         font-size:11px;padding:3px 8px;border-radius:4px;
                                         margin-right:6px;">{job['salary']}</span>
                            <span style="display:inline-block;background:#f3e8ff;color:#6b21a8;
                                         font-size:11px;padding:3px 8px;border-radius:4px;">
                                Posted {job['posted_date']}</span>
                        </td>
                    </tr>
                </table>

                <div style="font-size:13px;color:#4b5563;margin-top:10px;line-height:1.5;">
                    {job['description_snippet']}
                </div>

                <div style="margin-top:12px;">
                    <a href="{job['apply_link']}"
                       style="display:inline-block;background:#2563eb;color:#ffffff;
                              font-size:13px;font-weight:bold;padding:8px 20px;
                              border-radius:6px;text-decoration:none;">
                        Apply Now &rarr;</a>
                </div>
            </td></tr>
        </table>
    </td></tr>
    """


def build_jobs_email(jobs):
    """Build the full HTML email for job alerts.

    Args:
        jobs: list of job dicts from jobs_fetcher.fetch_jobs()

    Returns:
        (subject, html_body) tuple
    """
    date_str = _get_formatted_date()
    subject = f"Job Alert: {JOB_SEARCH_QUERY} - {date_str}"

    # Build job cards
    jobs_html = ""
    if jobs:
        for i, job in enumerate(jobs, 1):
            jobs_html += _build_job_card_html(job, i)
    else:
        jobs_html = """
        <tr><td style="padding:20px 30px;text-align:center;">
            <div style="background:#fef3c7;border-radius:8px;padding:20px;color:#92400e;
                        font-size:14px;">
                No new jobs matching your criteria were found in the last 2 days.
                Check back tomorrow!
            </div>
        </td></tr>
        """

    criteria_html = (
        f"<strong>Role:</strong> {JOB_SEARCH_QUERY} &bull; "
        f"<strong>Salary:</strong> ${JOB_MIN_SALARY:,}+ &bull; "
        f"<strong>Location:</strong> Remote (US)"
    )

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Georgia,serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:20px 0;">
<tr><td align="center">
<table width="640" cellpadding="0" cellspacing="0"
       style="background-color:#ffffff;border-radius:8px;overflow:hidden;
              box-shadow:0 2px 8px rgba(0,0,0,0.1);">

    <!-- Header -->
    <tr><td style="background:linear-gradient(135deg,#1e3a5f,#2563eb);padding:30px;
                   text-align:center;">
        <h1 style="color:#ffffff;font-size:26px;margin:0;letter-spacing:1px;">
            JOB ALERT</h1>
        <p style="color:#93c5fd;font-size:14px;margin:8px 0 0;letter-spacing:2px;">
            {date_str}</p>
    </td></tr>

    <!-- Search Criteria Banner -->
    <tr><td style="padding:16px 30px;background:#eff6ff;border-bottom:1px solid #dbeafe;">
        <div style="font-size:12px;color:#1e40af;text-align:center;">
            {criteria_html}
        </div>
    </td></tr>

    <!-- Job Count -->
    <tr><td style="padding:18px 30px 4px;">
        <h2 style="color:#1a1a2e;font-size:18px;margin:0;padding-bottom:8px;
                   border-bottom:2px solid #2563eb;">
            {len(jobs)} Job{'' if len(jobs) == 1 else 's'} Found (Last 2 Days)</h2>
    </td></tr>

    <!-- Job Listings -->
    {jobs_html}

    <!-- Footer -->
    <tr><td style="background:#1e3a5f;padding:20px;text-align:center;margin-top:20px;">
        <p style="color:#93c5fd;font-size:12px;margin:0;">
            Job Alert &mdash; Delivered every morning at 10:00 AM ET
        </p>
        <p style="color:#6b7280;font-size:11px;margin:6px 0 0;">
            Powered by JSearch &bull; Senior Financial Analyst &bull; Remote US
        </p>
    </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    return subject, html
