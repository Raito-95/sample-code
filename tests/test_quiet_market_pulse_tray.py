from personal_toolkit.quiet_market_pulse.models import InstrumentConfig, Quote
from personal_toolkit.quiet_market_pulse.sources import QuoteUnavailable
from personal_toolkit.quiet_market_pulse.tray import PulseState


def test_pulse_state_temporarily_reuses_then_expires_cached_quote(monkeypatch) -> None:
    now = [100.0]
    instrument = InstrumentConfig(
        label="BTC",
        symbol="BTCUSDT",
        source="binance",
        show_when_closed=True,
    )
    quote = Quote("BTC", "BTCUSDT", 100000, 1.0, "REGULAR")
    responses: list[Quote | Exception] = [quote, QuoteUnavailable("offline"), QuoteUnavailable("offline")]

    def fake_fetch_quote(_instrument: InstrumentConfig) -> Quote:
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(
        "personal_toolkit.quiet_market_pulse.tray.fetch_quote",
        fake_fetch_quote,
    )
    state = PulseState(stale_after_seconds=180, clock=lambda: now[0])

    assert state.update((instrument,)) == [quote]

    now[0] += 60
    assert state.update((instrument,)) == [quote]

    now[0] += 121
    assert state.update((instrument,)) == []
    assert state.last_quotes == {}
