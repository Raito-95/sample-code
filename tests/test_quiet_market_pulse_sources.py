import pytest

from personal_toolkit.quiet_market_pulse.models import InstrumentConfig
from personal_toolkit.quiet_market_pulse.sources import (
    _read_json,
    parse_binance_ticker_payload,
    parse_twse_quote_payload,
)


def test_parse_binance_ticker_payload() -> None:
    quote = parse_binance_ticker_payload(
        InstrumentConfig(label="BTC", symbol="BTCUSDT", source="binance", show_when_closed=True),
        {"lastPrice": "100000.12", "priceChangePercent": "-0.35"},
    )

    assert quote.label == "BTC"
    assert quote.price == 100000.12
    assert quote.change_percent == -0.35


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("lastPrice", "NaN"),
        ("lastPrice", "Infinity"),
        ("lastPrice", "0"),
        ("lastPrice", "-1"),
        ("priceChangePercent", "NaN"),
    ],
)
def test_parse_binance_ticker_payload_rejects_invalid_numbers(
    field: str,
    value: str,
) -> None:
    payload = {"lastPrice": "100000.12", "priceChangePercent": "-0.35"}
    payload[field] = value

    with pytest.raises(ValueError):
        parse_binance_ticker_payload(
            InstrumentConfig(label="BTC", symbol="BTCUSDT", source="binance"),
            payload,
        )


def test_parse_twse_quote_payload_marks_regular_during_taiwan_session() -> None:
    quote = parse_twse_quote_payload(
        {
            "rtcode": "0000",
            "msgArray": [
                {
                    "ch": "t00.tw",
                    "d": "20260511",
                    "n": "TAIEX",
                    "t": "10:55:05",
                    "y": "41603.94",
                    "z": "41965.40",
                }
            ],
            "queryTime": {"sysDate": "20260511", "sysTime": "10:55:14"},
        }
    )

    assert quote.symbol == "t00.tw"
    assert quote.price == 41965.40
    assert round(quote.change_percent or 0, 2) == 0.87
    assert quote.market_state == "REGULAR"


def test_parse_twse_quote_payload_marks_closed_outside_taiwan_session() -> None:
    quote = parse_twse_quote_payload(
        {
            "rtcode": "0000",
            "msgArray": [
                {
                    "ch": "t00.tw",
                    "d": "20260511",
                    "n": "TAIEX",
                    "t": "13:30:00",
                    "y": "41603.94",
                    "z": "41965.40",
                }
            ],
            "queryTime": {"sysDate": "20260511", "sysTime": "14:00:00"},
        }
    )

    assert quote.market_state == "CLOSED"


def test_read_json_rejects_unexpected_endpoint() -> None:
    try:
        _read_json("http://example.com/quote", 1.0, expected_host="example.com")
    except ValueError as exc:
        assert "unexpected quote endpoint" in str(exc)
    else:
        raise AssertionError("expected ValueError")
