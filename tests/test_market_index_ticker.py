import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

try:
    from PySide6.QtWidgets import QApplication
except ImportError as exc:
    pytest.skip(f"PySide6 QtWidgets unavailable: {exc}", allow_module_level=True)

from apps.market_index_ticker import (
    DOWN_COLOR,
    FLAT_COLOR,
    UP_COLOR,
    MarketPriceFeed,
    MarketTickerWidget,
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


def test_format_price_rules():
    assert MarketTickerWidget._format_price(999.12345) == "999.1235"
    assert MarketTickerWidget._format_price(1234.56) == "1,234.56"


def test_format_change_rules():
    assert MarketTickerWidget._format_change_pct(500.0, 100000.0) == "+0.50%"
    assert MarketTickerWidget._format_change_pct(-80.0, 4000.0) == "-2.00%"
    assert MarketTickerWidget._format_change_pct(0.0, 0.0) == "--"


def test_change_color_rules():
    assert MarketTickerWidget._change_color(1.0) == UP_COLOR
    assert MarketTickerWidget._change_color(-1.0) == DOWN_COLOR
    assert MarketTickerWidget._change_color(0.0) == FLAT_COLOR


def test_build_btc_payload_uses_24h_reference():
    payload = MarketPriceFeed._build_btc_payload(102000.0, 100000.0)
    assert payload == {
        "price": 102000.0,
        "reference": 100000.0,
        "change": 2000.0,
        "visible": True,
    }


def test_build_index_payload_shows_only_open_markets(monkeypatch):
    now_ts = 1_700_000_000
    monkeypatch.setattr(
        MarketPriceFeed,
        "_is_within_market_hours",
        staticmethod(lambda symbol, current_ts: symbol == "^DJI"),
    )

    visible_payload = MarketPriceFeed._build_index_payload(
        "^DJI",
        "Price 42,000.00 Prev. Close 41,850.00",
        now_ts,
    )
    hidden_payload = MarketPriceFeed._build_index_payload(
        "^GSPC",
        "Price 5,300.00 Prev. Close 5,320.00",
        now_ts,
    )

    assert visible_payload == {
        "price": 42000.0,
        "reference": 41850.0,
        "change": 150.0,
        "visible": True,
    }
    assert hidden_payload == {
        "price": 5300.0,
        "reference": 5320.0,
        "change": -20.0,
        "visible": False,
    }


def test_build_index_payload_uses_market_hours_fallback(monkeypatch):
    monkeypatch.setattr(
        MarketPriceFeed,
        "_is_within_market_hours",
        staticmethod(lambda symbol, current_ts: symbol == "^TWII"),
    )
    payload = MarketPriceFeed._build_index_payload(
        "^TWII",
        "Index Name Newest Index Change %Change Taiwan Stock Exchange Capitalization Weighted Stock Index 22,000.00 150.00 0.69%",
        1_741_659_200,
    )

    assert payload == {
        "price": 22000.0,
        "reference": 21850.0,
        "change": 150.0,
        "visible": True,
    }


def test_build_index_payload_hides_stale_financialcontent_quote_on_holiday(monkeypatch):
    monkeypatch.setattr(
        MarketPriceFeed,
        "_is_within_market_hours",
        staticmethod(lambda symbol, current_ts: True),
    )
    payload = MarketPriceFeed._build_index_payload(
        "^DJI",
        """
        <div>Price 42,000.00</div>
        <div>Prev. Close 41,850.00</div>
        <div>Daily Price Updated: 5:22 PM EST, Jan 16, 2026</div>
        """,
        1_737_313_200,
    )

    assert payload == {
        "price": 42000.0,
        "reference": 41850.0,
        "change": 150.0,
        "visible": False,
    }


def test_build_index_payload_keeps_current_financialcontent_quote_visible(monkeypatch):
    monkeypatch.setattr(
        MarketPriceFeed,
        "_is_within_market_hours",
        staticmethod(lambda symbol, current_ts: True),
    )
    payload = MarketPriceFeed._build_index_payload(
        "^DJI",
        """
        <div>Price 42,000.00</div>
        <div>Prev. Close 41,850.00</div>
        <div>Daily Price Updated: 10:05 AM EDT, Mar 17, 2026</div>
        """,
        1_773_756_300,
    )

    assert payload == {
        "price": 42000.0,
        "reference": 41850.0,
        "change": 150.0,
        "visible": True,
    }


def test_parse_financialcontent_quote():
    price, previous_close = MarketPriceFeed._parse_financialcontent_quote(
        "<div>Price 42,000.00</div><div>Prev. Close 41,850.00</div>"
    )
    assert price == 42000.0
    assert previous_close == 41850.0


def test_parse_taiwanindex_quote():
    price, previous_close = MarketPriceFeed._parse_taiwanindex_quote(
        """
        <div>Index Name Newest Index Change %Change</div>
        <div>Taiwan Stock Exchange Capitalization Weighted Stock Index 22,000.00 150.00 0.69%</div>
        """
    )
    assert price == 22000.0
    assert previous_close == 21850.0


def test_parse_taiwanindex_quote_detail_card_format():
    price, previous_close = MarketPriceFeed._parse_taiwanindex_quote(
        """
        <div>Taiwan Stock Exchange Capitalization Weighted Stock Index</div>
        <div>Newest Index：</div>
        <div>33,429.93</div>
        <div>Change：</div>
        <div>-259</div>
        <div>%Change：</div>
        <div>0%</div>
        """
    )
    assert price == 33429.93
    assert previous_close == 33688.93


def test_widget_hides_closed_markets_and_renders_change(qapp):
    widget = MarketTickerWidget(qapp)

    widget._on_prices_changed(
        {
            "BTC-USD": {
                "price": 100000.0,
                "reference": 98000.0,
                "change": 2000.0,
                "visible": True,
            },
            "^DJI": {
                "price": 42000.0,
                "reference": 41850.0,
                "change": 150.0,
                "visible": True,
            },
            "^GSPC": {
                "price": 5300.0,
                "reference": 5320.0,
                "change": -20.0,
                "visible": False,
            },
            "^IXIC": {
                "price": 17000.0,
                "reference": 17010.0,
                "change": -10.0,
                "visible": False,
            },
            "^TWII": {
                "price": 22000.0,
                "reference": 21850.0,
                "change": 150.0,
                "visible": True,
            },
        }
    )

    assert widget.items["BTC-USD"]["widget"].isHidden() is False
    assert widget.items["^DJI"]["widget"].isHidden() is False
    assert widget.items["^GSPC"]["widget"].isHidden() is True
    assert widget.items["^IXIC"]["widget"].isHidden() is True
    assert widget.items["^TWII"]["widget"].isHidden() is False
    assert widget.items["BTC-USD"]["price"].text() == "100,000.00"
    assert widget.items["BTC-USD"]["change"].text() == "+2.04%"
    assert UP_COLOR in widget.items["BTC-USD"]["change"].styleSheet()

    widget.feed.timer.stop()
    widget.feed.retry_timer.stop()
    widget.feed.ws.abort()
    widget.tray.hide()
    widget.close()


def test_widget_shrinks_when_only_btc_remains_visible(qapp, monkeypatch):
    monkeypatch.setattr(MarketPriceFeed, "start", lambda self: None)
    widget = MarketTickerWidget(qapp)
    widget.show()
    qapp.processEvents()

    widget._on_prices_changed(
        {
            "BTC-USD": {
                "price": 100000.0,
                "reference": 98000.0,
                "change": 2000.0,
                "visible": True,
            },
            "^DJI": {
                "price": 42000.0,
                "reference": 41850.0,
                "change": 150.0,
                "visible": True,
            },
            "^GSPC": {
                "price": 5300.0,
                "reference": 5320.0,
                "change": -20.0,
                "visible": False,
            },
            "^IXIC": {
                "price": 17000.0,
                "reference": 17010.0,
                "change": -10.0,
                "visible": False,
            },
            "^TWII": {
                "price": 22000.0,
                "reference": 21850.0,
                "change": 150.0,
                "visible": True,
            },
        }
    )
    qapp.processEvents()
    multi_item_size = widget.size()

    widget._on_prices_changed(
        {
            "BTC-USD": {
                "price": 100000.0,
                "reference": 98000.0,
                "change": 2000.0,
                "visible": True,
            },
            "^DJI": {
                "price": 42000.0,
                "reference": 41850.0,
                "change": 150.0,
                "visible": False,
            },
            "^GSPC": {
                "price": 5300.0,
                "reference": 5320.0,
                "change": -20.0,
                "visible": False,
            },
            "^IXIC": {
                "price": 17000.0,
                "reference": 17010.0,
                "change": -10.0,
                "visible": False,
            },
            "^TWII": {
                "price": 22000.0,
                "reference": 21850.0,
                "change": 150.0,
                "visible": False,
            },
        }
    )
    qapp.processEvents()
    btc_only_size = widget.size()

    assert btc_only_size.height() < multi_item_size.height()
    assert btc_only_size.width() <= multi_item_size.width()

    widget.tray.hide()
    widget.close()
