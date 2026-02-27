import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "coreyely1@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", GMAIL_ADDRESS)
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")

# News RSS feeds
NEWS_SOURCES = {
    "Top US News": {
        "feeds": [
            "https://feeds.npr.org/1001/rss.xml",
            "https://news.google.com/rss/search?q=United+States+news+when:1d&hl=en-US&gl=US&ceid=US:en",
        ],
        "count": 5,
    },
    "Top European News": {
        "feeds": [
            "https://news.google.com/rss/search?q=Europe+news+when:1d&hl=en-US&gl=US&ceid=US:en",
        ],
        "count": 5,
    },
    "Top African News": {
        "feeds": [
            "https://news.google.com/rss/search?q=Africa+news+when:1d&hl=en-US&gl=US&ceid=US:en",
        ],
        "count": 5,
    },
    "Top China News": {
        "feeds": [
            "https://news.google.com/rss/search?q=China+news+when:1d&hl=en-US&gl=US&ceid=US:en",
        ],
        "count": 5,
    },
    "English Premier League News": {
        "feeds": [
            "https://news.google.com/rss/search?q=%22Premier+League%22+when:1d&hl=en-US&gl=US&ceid=US:en",
        ],
        "count": 3,
    },
    "West Ham United News": {
        "feeds": [
            "https://news.google.com/rss/search?q=%22West+Ham%22+Premier+League+OR+transfer+OR+match+OR+manager+when:3d&hl=en-US&gl=US&ceid=US:en",
        ],
        "count": 2,
    },
}

# ESPN API endpoints for scores
SCORE_ENDPOINTS = {
    "English Premier League": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
    "Champions League": "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/scoreboard",
    "Europa League": "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.europa/scoreboard",
    "FA Cup": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.fa/scoreboard",
    "Carabao Cup": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.league_cup/scoreboard",
    "EFL Championship": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.2/scoreboard",
    "NBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "College Football": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
    "College Basketball": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard",
}

# College sports filter: only show games where at least one team is
# ranked in the Top 25 or is one of these favorite teams.
COLLEGE_LEAGUES = {"College Football", "College Basketball"}
COLLEGE_FAVORITE_TEAMS = {"Oregon Ducks"}

# Only include articles from these news sources
ALLOWED_NEWS_SOURCES = {
    "NPR",
    "ABC News",
    "NBC News",
    "The Associated Press",
    "AP News",
    "Reuters",
    "Forbes",
    "The Wall Street Journal",
    "WSJ",
    "The New York Times",
    "New York Times",
    "The Hill",
}
