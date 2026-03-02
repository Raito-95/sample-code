import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from apps.crypto_price_ticker import PriceFeed, TickerWidget


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


def test_format_price_rules():
    assert TickerWidget._format_price(999.12345) == "999.1235"
    assert TickerWidget._format_price(1234.56) == "1,234.56"


def test_price_feed_parses_stream_messages(qapp):
    feed = PriceFeed()
    captured = []
    feed.prices_changed.connect(lambda btc, eth: captured.append((btc, eth)))

    feed._on_message('{"stream":"btcusdt@trade","data":{"p":"100000.00"}}')
    feed._on_message('{"stream":"ethusdt@trade","data":{"p":"2500.50"}}')

    assert captured[-1] == (100000.0, 2500.5)


def test_price_feed_ignores_invalid_payload(qapp):
    feed = PriceFeed()
    captured = []
    feed.prices_changed.connect(lambda btc, eth: captured.append((btc, eth)))

    feed._on_message("not-json")
    feed._on_message('{"stream":"unknown@trade","data":{"p":"1"}}')
    feed._on_message('{"stream":"btcusdt@trade","data":{}}')

    assert captured == []

