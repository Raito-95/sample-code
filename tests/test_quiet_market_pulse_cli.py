from personal_toolkit.quiet_market_pulse.formatting import compact_summary
from personal_toolkit.quiet_market_pulse.models import Quote


def test_compact_summary() -> None:
    assert compact_summary([Quote("BTC", "BTCUSDT", 100000.0, 1.23)]) == "BTC 100,000.00 +1.23%"
