from personal_toolkit.quiet_market_pulse.formatting import format_percent, format_price, format_quote_line
from personal_toolkit.quiet_market_pulse.models import Quote


def test_format_price() -> None:
    assert format_price(23456.789) == "23,456.79"
    assert format_price(123.456) == "123.46"
    assert format_price(0.123456) == "0.1235"


def test_format_percent() -> None:
    assert format_percent(0.5) == "+0.50%"
    assert format_percent(-1.25) == "-1.25%"
    assert format_percent(None) == "--"


def test_format_quote_line() -> None:
    quote = Quote(label="BTC", symbol="BTCUSDT", price=100000.0, change_percent=1.5)

    assert format_quote_line(quote) == "BTC 100,000.00 +1.50%"
