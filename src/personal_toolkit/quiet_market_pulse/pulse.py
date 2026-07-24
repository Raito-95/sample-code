from __future__ import annotations

from collections.abc import Callable

from personal_toolkit.quiet_market_pulse.models import InstrumentConfig, PulseConfig, Quote
from personal_toolkit.quiet_market_pulse.sources import QuoteUnavailable, fetch_quote


QuoteFetcher = Callable[[InstrumentConfig], Quote]


def is_visible(instrument: InstrumentConfig, quote: Quote) -> bool:
    if instrument.show_when_closed:
        return True
    return quote.market_state == "REGULAR"


def collect_visible_quotes(
    config: PulseConfig,
    fetcher: QuoteFetcher = fetch_quote,
) -> list[Quote]:
    quotes: list[Quote] = []
    for instrument in config.instruments:
        try:
            quote = fetcher(instrument)
        except QuoteUnavailable:
            continue
        if is_visible(instrument, quote):
            quotes.append(quote)
    return quotes
