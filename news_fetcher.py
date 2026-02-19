import requests
import xml.etree.ElementTree as ET
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from config import NEWS_SOURCES

logger = logging.getLogger(__name__)

# Common RSS namespaces
NAMESPACES = {
    "media": "http://search.yahoo.com/mrss/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "atom": "http://www.w3.org/2005/Atom",
}


def _parse_published(item):
    """Extract a datetime from an RSS item's pubDate or dc:date."""
    for tag in ["pubDate", "{http://purl.org/dc/elements/1.1/}date"]:
        elem = item.find(tag)
        if elem is not None and elem.text:
            try:
                return parsedate_to_datetime(elem.text.strip())
            except Exception:
                pass
    return datetime.now(tz=timezone.utc)


def _extract_source(item, feed_title=""):
    """Try to extract source name from an RSS item."""
    source_elem = item.find("source")
    if source_elem is not None and source_elem.text:
        return source_elem.text.strip()
    if feed_title:
        for suffix in [" - RSS", " RSS", " Feed"]:
            feed_title = feed_title.replace(suffix, "")
        return feed_title
    return ""


def _deduplicate(articles):
    """Remove duplicate articles based on title similarity."""
    seen_titles = set()
    unique = []
    for article in articles:
        normalized = article["title"].lower().strip()
        if normalized in seen_titles:
            continue
        is_dup = False
        for seen in seen_titles:
            if normalized in seen or seen in normalized:
                is_dup = True
                break
        if not is_dup:
            seen_titles.add(normalized)
            unique.append(article)
    return unique


def _parse_rss_feed(xml_text):
    """Parse RSS XML text and return (feed_title, list_of_item_elements)."""
    root = ET.fromstring(xml_text)

    # Standard RSS 2.0
    channel = root.find("channel")
    if channel is not None:
        feed_title = ""
        title_elem = channel.find("title")
        if title_elem is not None and title_elem.text:
            feed_title = title_elem.text.strip()
        items = channel.findall("item")
        return feed_title, items

    # Atom feed fallback
    if root.tag == "{http://www.w3.org/2005/Atom}feed":
        feed_title = ""
        title_elem = root.find("{http://www.w3.org/2005/Atom}title")
        if title_elem is not None and title_elem.text:
            feed_title = title_elem.text.strip()
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        return feed_title, entries

    return "", []


def _extract_item_fields(item):
    """Extract title, link, and description from an RSS item or Atom entry."""
    # RSS item
    title_elem = item.find("title")
    link_elem = item.find("link")
    desc_elem = item.find("description")

    title = (title_elem.text or "Untitled") if title_elem is not None else "Untitled"
    link = (link_elem.text or "") if link_elem is not None else ""
    description = (desc_elem.text or "") if desc_elem is not None else ""

    # Atom entry fallback
    if not link:
        atom_link = item.find("{http://www.w3.org/2005/Atom}link")
        if atom_link is not None:
            link = atom_link.get("href", "")
    if title == "Untitled":
        atom_title = item.find("{http://www.w3.org/2005/Atom}title")
        if atom_title is not None and atom_title.text:
            title = atom_title.text

    return title.strip(), link.strip(), description.strip()


def fetch_news_section(section_name, feed_urls, count):
    """Fetch news articles from the given RSS feed URLs.

    Returns a list of dicts: [{"title", "link", "source", "published", "description"}, ...]
    """
    all_articles = []

    for url in feed_urls:
        try:
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; DailyDigest/1.0)",
            })
            resp.raise_for_status()
            feed_title, items = _parse_rss_feed(resp.text)

            for item in items:
                title, link, description = _extract_item_fields(item)
                article = {
                    "title": title,
                    "link": link,
                    "source": _extract_source(item, feed_title),
                    "published": _parse_published(item),
                    "description": description,
                }
                all_articles.append(article)
        except Exception as e:
            logger.warning(f"Failed to fetch feed {url}: {e}")

    # Sort by published date (newest first), deduplicate, then take top N
    all_articles.sort(key=lambda a: a["published"], reverse=True)
    all_articles = _deduplicate(all_articles)
    return all_articles[:count]


def fetch_all_news():
    """Fetch all news sections defined in config.

    Returns a dict: {"Section Name": [articles], ...}
    """
    results = {}
    for section_name, cfg in NEWS_SOURCES.items():
        logger.info(f"Fetching {section_name}...")
        articles = fetch_news_section(section_name, cfg["feeds"], cfg["count"])
        results[section_name] = articles
        logger.info(f"  Got {len(articles)} articles for {section_name}")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    news = fetch_all_news()
    for section, articles in news.items():
        print(f"\n{'='*60}")
        print(f"  {section}")
        print(f"{'='*60}")
        for i, a in enumerate(articles, 1):
            print(f"  {i}. {a['title']}")
            print(f"     {a['source']} | {a['link']}")
