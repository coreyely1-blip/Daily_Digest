import requests
import logging
from datetime import datetime, timedelta, timezone
from config import SCORE_ENDPOINTS

logger = logging.getLogger(__name__)


def _fetch_scoreboard(url, date_str):
    """Fetch scoreboard data from ESPN API for a given date (YYYYMMDD)."""
    try:
        resp = requests.get(url, params={"dates": date_str}, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to fetch {url} for {date_str}: {e}")
        return None


def _parse_soccer_event(event):
    """Parse a soccer event into a score dict."""
    competition = event.get("competitions", [{}])[0]
    status_info = competition.get("status", {})
    status_type = status_info.get("type", {})

    # Only include completed games
    if not status_type.get("completed", False):
        return None

    competitors = competition.get("competitors", [])
    if len(competitors) < 2:
        return None

    home = away = None
    for c in competitors:
        if c.get("homeAway") == "home":
            home = c
        else:
            away = c

    if not home or not away:
        return None

    # Extract goal details if available
    details = competition.get("details", [])
    goal_scorers = []
    for detail in details:
        if detail.get("scoringPlay"):
            athletes = detail.get("athletesInvolved", [])
            clock = detail.get("clock", {}).get("displayValue", "")
            if athletes:
                scorer_name = athletes[0].get("displayName", "Unknown")
                goal_scorers.append(f"{scorer_name} ({clock})")

    return {
        "home_team": home["team"]["displayName"],
        "away_team": away["team"]["displayName"],
        "home_score": home.get("score", "0"),
        "away_score": away.get("score", "0"),
        "status": status_type.get("shortDetail", "FT"),
        "goal_scorers": goal_scorers,
    }


def _parse_basketball_event(event):
    """Parse a basketball event into a score dict."""
    competition = event.get("competitions", [{}])[0]
    status_info = competition.get("status", {})
    status_type = status_info.get("type", {})

    if not status_type.get("completed", False):
        return None

    competitors = competition.get("competitors", [])
    if len(competitors) < 2:
        return None

    home = away = None
    for c in competitors:
        if c.get("homeAway") == "home":
            home = c
        else:
            away = c

    if not home or not away:
        return None

    return {
        "home_team": home["team"]["displayName"],
        "away_team": away["team"]["displayName"],
        "home_score": home.get("score", "0"),
        "away_score": away.get("score", "0"),
        "status": status_type.get("shortDetail", "Final"),
    }


def _parse_football_event(event):
    """Parse a college football event into a score dict (same format as basketball)."""
    return _parse_basketball_event(event)


def fetch_scores_for_league(league_name, endpoint_url):
    """Fetch completed scores for a league over the past 24 hours.

    Checks both yesterday and today's date to cover the full window.
    """
    now = datetime.now(tz=timezone.utc)
    yesterday = now - timedelta(days=1)
    dates_to_check = [
        yesterday.strftime("%Y%m%d"),
        now.strftime("%Y%m%d"),
    ]

    all_scores = []
    seen_event_ids = set()

    is_soccer = league_name in (
        "English Premier League",
        "Champions League",
        "Europa League",
        "FA Cup",
        "Carabao Cup",
        "EFL Championship",
    )

    for date_str in dates_to_check:
        data = _fetch_scoreboard(endpoint_url, date_str)
        if not data:
            continue

        events = data.get("events", [])
        for event in events:
            event_id = event.get("id")
            if event_id in seen_event_ids:
                continue
            seen_event_ids.add(event_id)

            if is_soccer:
                score = _parse_soccer_event(event)
            else:
                score = _parse_basketball_event(event)

            if score:
                all_scores.append(score)

    return all_scores


def fetch_all_scores():
    """Fetch scores for all configured leagues.

    Returns a dict: {"League Name": [scores], ...}
    Only includes leagues that had completed games.
    """
    results = {}
    for league_name, url in SCORE_ENDPOINTS.items():
        logger.info(f"Fetching scores for {league_name}...")
        scores = fetch_scores_for_league(league_name, url)
        if scores:
            results[league_name] = scores
            logger.info(f"  Got {len(scores)} completed games for {league_name}")
        else:
            logger.info(f"  No completed games for {league_name}")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scores = fetch_all_scores()
    for league, games in scores.items():
        print(f"\n{'='*60}")
        print(f"  {league}")
        print(f"{'='*60}")
        for g in games:
            print(f"  {g['home_team']} {g['home_score']} - {g['away_score']} {g['away_team']}")
            if g.get("goal_scorers"):
                print(f"    Goals: {', '.join(g['goal_scorers'])}")
