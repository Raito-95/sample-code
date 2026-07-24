from __future__ import annotations

from personal_toolkit.quiet_market_pulse.models import Quote


def format_price(value: float) -> str:
    if abs(value) >= 1000:
        return f"{value:,.2f}"
    if abs(value) >= 10:
        return f"{value:.2f}"
    return f"{value:.4f}"


def format_percent(value: float | None) -> str:
    if value is None:
        return "--"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def format_quote_line(quote: Quote) -> str:
    return f"{quote.label} {format_price(quote.price)} {format_percent(quote.change_percent)}"


def compact_summary(quotes: list[Quote]) -> str:
    if not quotes:
        return "No open market data"
    return " | ".join(format_quote_line(quote) for quote in quotes)
