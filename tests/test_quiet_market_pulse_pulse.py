from personal_toolkit.quiet_market_pulse.models import InstrumentConfig, PulseConfig, Quote
from personal_toolkit.quiet_market_pulse.pulse import collect_visible_quotes, is_visible
from personal_toolkit.quiet_market_pulse.sources import QuoteUnavailable


def test_stock_index_visible_only_when_regular() -> None:
    instrument = InstrumentConfig(label="TWII", symbol="^TWII", source="twse")

    assert is_visible(instrument, Quote("TWII", "^TWII", 24000, 0.1, "REGULAR")) is True
    assert is_visible(instrument, Quote("TWII", "^TWII", 24000, 0.1, "CLOSED")) is False


def test_btc_visible_when_closed_flag_enabled() -> None:
    instrument = InstrumentConfig(
        label="BTC",
        symbol="BTCUSDT",
        source="binance",
        show_when_closed=True,
    )

    assert is_visible(instrument, Quote("BTC", "BTCUSDT", 100000, 0.1, "CLOSED")) is True


def test_collect_visible_quotes_skips_unavailable_quote() -> None:
    config = PulseConfig(
        refresh_seconds=60,
        instruments=(InstrumentConfig(label="TWII", symbol="^TWII", source="twse"),),
    )

    def fetcher(_instrument: InstrumentConfig) -> Quote:
        raise QuoteUnavailable("network unavailable")

    assert collect_visible_quotes(config, fetcher=fetcher) == []
