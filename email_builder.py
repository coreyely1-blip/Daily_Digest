from datetime import datetime
import pytz
from config import TIMEZONE


def _get_formatted_date():
    """Get today's date formatted for the email subject/header."""
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    return now.strftime("%A, %B %d, %Y")


def _build_news_section_html(section_name, articles):
    """Build HTML for a single news section."""
    if not articles:
        return f"""
        <tr><td style="padding:20px 30px 5px;">
            <h2 style="color:#1a1a2e;font-size:20px;margin:0;padding-bottom:8px;
                       border-bottom:2px solid #e94560;">{section_name}</h2>
        </td></tr>
        <tr><td style="padding:5px 30px 15px;color:#666;font-style:italic;">
            No stories available at this time.
        </td></tr>
        """

    rows = ""
    for i, article in enumerate(articles, 1):
        source_badge = ""
        if article.get("source"):
            source_badge = (
                f'<span style="display:inline-block;background:#e8e8e8;color:#555;'
                f'font-size:11px;padding:2px 8px;border-radius:3px;margin-left:8px;">'
                f'{article["source"]}</span>'
            )

        rows += f"""
        <tr><td style="padding:4px 30px 4px 45px;">
            <span style="color:#333;font-size:14px;">
                {i}. <a href="{article['link']}" style="color:#1a1a2e;text-decoration:none;">
                    {article['title']}</a>{source_badge}
            </span>
        </td></tr>
        """

    return f"""
    <tr><td style="padding:20px 30px 5px;">
        <h2 style="color:#1a1a2e;font-size:20px;margin:0;padding-bottom:8px;
                   border-bottom:2px solid #e94560;">{section_name}</h2>
    </td></tr>
    {rows}
    """


def _build_soccer_score_html(game):
    """Build HTML for a single soccer score."""
    scorers_html = ""
    if game.get("goal_scorers"):
        scorers = ", ".join(game["goal_scorers"])
        scorers_html = (
            f'<div style="font-size:11px;color:#888;margin-top:2px;">'
            f'Goals: {scorers}</div>'
        )

    return f"""
    <tr><td style="padding:3px 30px 3px 45px;">
        <div style="font-size:14px;color:#333;">
            <strong>{game['home_team']}</strong> {game['home_score']} &ndash;
            {game['away_score']} <strong>{game['away_team']}</strong>
            <span style="color:#888;font-size:12px;margin-left:6px;">{game['status']}</span>
        </div>
        {scorers_html}
    </td></tr>
    """


def _build_basketball_score_html(game):
    """Build HTML for a single basketball/football score."""
    return f"""
    <tr><td style="padding:3px 30px 3px 45px;">
        <div style="font-size:14px;color:#333;">
            <strong>{game['away_team']}</strong> {game['away_score']} @
            <strong>{game['home_team']}</strong> {game['home_score']}
            <span style="color:#888;font-size:12px;margin-left:6px;">{game['status']}</span>
        </div>
    </td></tr>
    """


def _build_scores_section_html(all_scores):
    """Build the full scores section HTML."""
    if not all_scores:
        return """
        <tr><td style="padding:20px 30px 5px;">
            <h2 style="color:#1a1a2e;font-size:20px;margin:0;padding-bottom:8px;
                       border-bottom:2px solid #16213e;">SCORES (Past 24 Hours)</h2>
        </td></tr>
        <tr><td style="padding:5px 30px 15px;color:#666;font-style:italic;">
            No completed games in the past 24 hours.
        </td></tr>
        """

    soccer_leagues = {
        "English Premier League", "Champions League", "Europa League",
        "FA Cup", "Carabao Cup", "EFL Championship",
    }

    html = """
    <tr><td style="padding:25px 30px 5px;">
        <h2 style="color:#1a1a2e;font-size:20px;margin:0;padding-bottom:8px;
                   border-bottom:2px solid #16213e;">SCORES (Past 24 Hours)</h2>
    </td></tr>
    """

    for league_name, games in all_scores.items():
        html += f"""
        <tr><td style="padding:12px 30px 4px 30px;">
            <h3 style="color:#e94560;font-size:16px;margin:0;">{league_name}</h3>
        </td></tr>
        """
        for game in games:
            if league_name in soccer_leagues:
                html += _build_soccer_score_html(game)
            else:
                html += _build_basketball_score_html(game)

    return html


def build_email(news_data, scores_data):
    """Build the full HTML email.

    Args:
        news_data: dict from fetch_all_news() - {"Section Name": [articles]}
        scores_data: dict from fetch_all_scores() - {"League Name": [scores]}

    Returns:
        (subject, html_body) tuple
    """
    date_str = _get_formatted_date()
    subject = f"Daily Digest - {date_str}"

    # Build news sections
    news_html = ""
    for section_name, articles in news_data.items():
        news_html += _build_news_section_html(section_name, articles)

    # Build scores section
    scores_html = _build_scores_section_html(scores_data)

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
    <tr><td style="background:#1a1a2e;padding:30px;text-align:center;">
        <h1 style="color:#ffffff;font-size:28px;margin:0;letter-spacing:1px;">
            DAILY DIGEST</h1>
        <p style="color:#e94560;font-size:14px;margin:8px 0 0;letter-spacing:2px;">
            {date_str}</p>
    </td></tr>

    <!-- News Sections -->
    {news_html}

    <!-- Divider -->
    <tr><td style="padding:15px 30px;">
        <hr style="border:none;border-top:3px double #1a1a2e;">
    </td></tr>

    <!-- Scores Section -->
    {scores_html}

    <!-- Footer -->
    <tr><td style="background:#1a1a2e;padding:20px;text-align:center;margin-top:20px;">
        <p style="color:#888;font-size:12px;margin:0;">
            Daily Digest &mdash; Delivered every morning at 7:00 AM ET
        </p>
    </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    return subject, html
