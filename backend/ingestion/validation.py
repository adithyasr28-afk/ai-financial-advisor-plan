from collections.abc import Iterable
from .models import MarketBar, MacroObservation, NewsItem, Quote


def validate_market_bars(bars: Iterable[MarketBar]) -> list[MarketBar]:
    result = list(bars)
    for bar in result:
        if bar.low > bar.high or not (bar.low <= bar.open <= bar.high) or not (bar.low <= bar.close <= bar.high):
            raise ValueError(f"invalid OHLC range for {bar.symbol} at {bar.timestamp}")
    return result


def validate_quote(quote: Quote) -> Quote:
    if quote.low > quote.high or not (quote.low <= quote.price <= quote.high):
        raise ValueError(f"invalid quote range for {quote.symbol}")
    return quote


def validate_macro(observations: Iterable[MacroObservation]) -> list[MacroObservation]:
    result = list(observations)
    if any(observation.value != observation.value for observation in result):
        raise ValueError("macro observation contains NaN")
    return result


def validate_news(items: Iterable[NewsItem]) -> list[NewsItem]:
    result = list(items)
    if any(not item.title.strip() or not item.link.startswith("http") for item in result):
        raise ValueError("news item requires a title and absolute link")
    return result
