from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree
from ..models import NewsItem
from ..validation import validate_news
from ..http import get_bytes


def parse_rss(text: str) -> list[NewsItem]:
    root = ElementTree.fromstring(text)
    items = []
    for item in root.findall("./channel/item"):
        published = item.findtext("pubDate")
        items.append(NewsItem(source="rss", title=item.findtext("title") or "", link=item.findtext("link") or "", published_at=parsedate_to_datetime(published) if published else None, summary=item.findtext("description")))
    return validate_news(items)


def parse_fixture(path: Path) -> list[NewsItem]:
    return parse_rss(path.read_text(encoding="utf-8"))


def fetch_rss(symbol: str = "AAPL") -> list[NewsItem]:
    payload = get_bytes(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US")
    return parse_rss(payload.decode("utf-8"))
