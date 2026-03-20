import json
import re
import sys
from datetime import datetime, timedelta, timezone
from html import unescape

from PySide6.QtCore import QObject, QPoint, QDateTime, QTimer, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QColor, QFont, QGuiApplication, QIcon, QPixmap
from PySide6.QtNetwork import QAbstractSocket, QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMenu,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

TICKERS = {
    "BTC-USD": {
        "label": "BTC",
        "always_visible": True,
        "source": "binance",
    },
    "^DJI": {
        "label": "DJI",
        "always_visible": False,
        "source": "financialcontent",
        "url": "https://markets.financialcontent.com/stocks/quote?Symbol=DJI%3ADJI",
    },
    "^GSPC": {
        "label": "S&P",
        "always_visible": False,
        "source": "financialcontent",
        "url": "https://markets.financialcontent.com/stocks/quote?Symbol=CBOE%3ASPX",
    },
    "^IXIC": {
        "label": "NASDAQ",
        "always_visible": False,
        "source": "financialcontent",
        "url": "https://markets.financialcontent.com/stocks/quote?Symbol=NQ%3ACOMP",
    },
    "^TWII": {
        "label": "TAIEX",
        "always_visible": False,
        "source": "taiwanindex",
        "url": "https://taiwanindex.com.tw/en/indexes/board/twse",
    },
}

MARKET_SCHEDULES = {
    "^DJI": {"market": "us", "open": (9, 30), "close": (16, 0)},
    "^GSPC": {"market": "us", "open": (9, 30), "close": (16, 0)},
    "^IXIC": {"market": "us", "open": (9, 30), "close": (16, 0)},
    "^TWII": {"market": "tw", "open": (9, 0), "close": (13, 30)},
}

TAIWAN_INDEX_NAME = "Taiwan Stock Exchange Capitalization Weighted Stock Index"
INDEX_SYMBOLS = [symbol for symbol, config in TICKERS.items() if config["source"] != "binance"]
BINANCE_STREAM = "wss://stream.binance.com:9443/ws/btcusdt@ticker"

UP_COLOR = "#7bd88f"
DOWN_COLOR = "#ff6b6b"
FLAT_COLOR = "#b8c1d1"


class MarketPriceFeed(QObject):
    prices_changed = Signal(dict)
    status_changed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self._on_reply_finished)

        self.ws = QWebSocket()
        self.ws.connected.connect(self._on_btc_connected)
        self.ws.disconnected.connect(self._on_btc_disconnected)
        self.ws.textMessageReceived.connect(self._on_btc_message)

        self.timer = QTimer(self)
        self.timer.setInterval(15000)
        self.timer.timeout.connect(self.fetch_indices)

        self.retry_timer = QTimer(self)
        self.retry_timer.setInterval(5000)
        self.retry_timer.timeout.connect(self._connect_btc)

        self._request_in_flight = False
        self._pending_symbols: set[str] = set()
        self._results = self._empty_results()
        self._btc_connected = False
        self._index_error = False

    def start(self) -> None:
        self.fetch_indices()
        self._connect_btc()
        if not self.timer.isActive():
            self.timer.start()

    def fetch_indices(self) -> None:
        if self._request_in_flight:
            return

        self._request_in_flight = True
        self._pending_symbols = set(INDEX_SYMBOLS)
        for symbol in INDEX_SYMBOLS:
            config = TICKERS[symbol]
            request = QNetworkRequest(QUrl(config["url"]))
            request.setRawHeader(b"User-Agent", b"Mozilla/5.0")
            reply = self.manager.get(request)
            reply.setProperty("symbol", symbol)

        self._emit_status()

    def _connect_btc(self) -> None:
        if self.ws.state() in (
            QAbstractSocket.SocketState.ConnectedState,
            QAbstractSocket.SocketState.ConnectingState,
        ):
            return
        self.ws.open(QUrl(BINANCE_STREAM))
        self._emit_status()

    def _on_btc_connected(self) -> None:
        self._btc_connected = True
        self.retry_timer.stop()
        self._emit_status()

    def _on_btc_disconnected(self) -> None:
        self._btc_connected = False
        if not self.retry_timer.isActive():
            self.retry_timer.start()
        self._emit_status()

    def _on_btc_message(self, message: str) -> None:
        try:
            payload = json.loads(message)
            price = float(payload.get("c") or 0.0)
            reference = float(payload.get("o") or 0.0)
        except (TypeError, ValueError, json.JSONDecodeError):
            return

        self._results["BTC-USD"] = self._build_btc_payload(price, reference)
        self.prices_changed.emit(self._merge_results())
        self._emit_status()

    def _on_reply_finished(self, reply: QNetworkReply) -> None:
        symbol = str(reply.property("symbol") or "")

        if reply.error() != QNetworkReply.NetworkError.NoError:
            if symbol:
                self._results[symbol] = self._empty_item()
            self._finalize_reply(reply, had_error=True)
            return

        try:
            raw_text = bytes(reply.readAll()).decode("utf-8", errors="ignore")
            self._results[symbol] = self._build_index_payload(
                symbol,
                raw_text,
                QDateTime.currentSecsSinceEpoch(),
            )
        except (KeyError, IndexError, TypeError, ValueError):
            if symbol:
                self._results[symbol] = self._empty_item()
            self._finalize_reply(reply, had_error=True)
            return
        self._finalize_reply(reply, had_error=False)

    def _finalize_reply(self, reply: QNetworkReply, had_error: bool) -> None:
        symbol = str(reply.property("symbol") or "")
        if symbol:
            self._pending_symbols.discard(symbol)

        if self._pending_symbols:
            reply.deleteLater()
            return

        self._request_in_flight = False
        self._index_error = had_error
        self.prices_changed.emit(self._merge_results())
        self._emit_status()
        reply.deleteLater()

    def _emit_status(self) -> None:
        if self._btc_connected and not self._request_in_flight and not self._index_error:
            self.status_changed.emit("connected")
            return
        if self._btc_connected and self._request_in_flight:
            self.status_changed.emit("updating")
            return
        if self._btc_connected and self._index_error:
            self.status_changed.emit("btc live")
            return
        if self._request_in_flight:
            self.status_changed.emit("updating")
            return
        self.status_changed.emit("reconnecting")

    @staticmethod
    def _empty_item() -> dict[str, float | bool]:
        return {"price": 0.0, "reference": 0.0, "change": 0.0, "visible": False}

    def _empty_results(self) -> dict[str, dict[str, float | bool]]:
        return {symbol: self._empty_item() for symbol in TICKERS}

    @staticmethod
    def _build_btc_payload(price: float, reference: float) -> dict[str, float | bool]:
        if price <= 0 or reference <= 0:
            return {"price": 0.0, "reference": 0.0, "change": 0.0, "visible": False}
        return {
            "price": price,
            "reference": reference,
            "change": price - reference,
            "visible": True,
        }

    @staticmethod
    def _build_index_payload(
        symbol: str, raw_text: str, now_ts: int
    ) -> dict[str, float | bool]:
        config = TICKERS[symbol]
        if config["source"] == "financialcontent":
            price, reference = MarketPriceFeed._parse_financialcontent_quote(raw_text)
            has_current_quote = MarketPriceFeed._has_current_financialcontent_quote(raw_text, now_ts)
        elif config["source"] == "taiwanindex":
            price, reference = MarketPriceFeed._parse_taiwanindex_quote(raw_text)
            has_current_quote = True
        else:
            return {"price": 0.0, "reference": 0.0, "change": 0.0, "visible": False}

        if price <= 0 or reference <= 0:
            return {"price": 0.0, "reference": 0.0, "change": 0.0, "visible": False}

        visible = has_current_quote and MarketPriceFeed._is_within_market_hours(symbol, now_ts)
        return {
            "price": price,
            "reference": reference,
            "change": price - reference,
            "visible": visible,
        }

    @staticmethod
    def _parse_financialcontent_quote(raw_text: str) -> tuple[float, float]:
        text = MarketPriceFeed._normalize_text(raw_text)
        price_match = re.search(r"Price\s+([0-9,]+(?:\.[0-9]+)?)", text)
        prev_close_match = re.search(r"Prev\.\s*Close\s+([0-9,]+(?:\.[0-9]+)?)", text)
        if not price_match or not prev_close_match:
            raise ValueError("financialcontent quote fields missing")
        return (
            float(price_match.group(1).replace(",", "")),
            float(prev_close_match.group(1).replace(",", "")),
        )

    @staticmethod
    def _has_current_financialcontent_quote(raw_text: str, now_ts: int) -> bool:
        market_date = MarketPriceFeed._market_local_datetime("us", now_ts).date()
        quote_date = MarketPriceFeed._parse_financialcontent_quote_date(raw_text)
        if quote_date is None:
            return True
        return quote_date == market_date

    @staticmethod
    def _parse_financialcontent_quote_date(raw_text: str):
        text = MarketPriceFeed._normalize_text(raw_text)
        match = re.search(
            r"Daily Price Updated:\s+\d{1,2}:\d{2}\s+[AP]M\s+(?:EST|EDT),\s+([A-Za-z]{3}\s+\d{1,2},\s+\d{4})",
            text,
        )
        if not match:
            return None
        return datetime.strptime(match.group(1), "%b %d, %Y").date()

    @staticmethod
    def _parse_taiwanindex_quote(raw_text: str) -> tuple[float, float]:
        text = MarketPriceFeed._normalize_text(raw_text)
        summary_pattern = (
            re.escape(TAIWAN_INDEX_NAME)
            + r"\s+([0-9,]+(?:\.[0-9]+)?)\s+([+-]?[0-9,]+(?:\.[0-9]+)?)\s+([+-]?[0-9]+(?:\.[0-9]+)?)%"
        )
        match = re.search(summary_pattern, text)
        if not match:
            detail_pattern = (
                re.escape(TAIWAN_INDEX_NAME)
                + r"\s+Newest Index[:：]?\s*([0-9,]+(?:\.[0-9]+)?)\s+Change[:：]?\s*([+-]?[0-9,]+(?:\.[0-9]+)?)\s+%Change[:：]?\s*([+-]?[0-9]+(?:\.[0-9]+)?)%"
            )
            match = re.search(detail_pattern, text)
        if not match:
            raise ValueError("taiwanindex quote fields missing")
        price = float(match.group(1).replace(",", ""))
        change = float(match.group(2).replace(",", ""))
        return (price, price - change)

    @staticmethod
    def _normalize_text(raw_text: str) -> str:
        text = re.sub(r"<script.*?</script>", " ", raw_text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _is_within_market_hours(symbol: str, now_ts: int) -> bool:
        schedule = MARKET_SCHEDULES.get(symbol)
        if not schedule:
            return False

        now = MarketPriceFeed._market_local_datetime(schedule["market"], now_ts)
        if now.weekday() >= 5:
            return False

        now_minutes = now.hour * 60 + now.minute
        open_minutes = schedule["open"][0] * 60 + schedule["open"][1]
        close_minutes = schedule["close"][0] * 60 + schedule["close"][1]
        return open_minutes <= now_minutes < close_minutes

    @staticmethod
    def _market_utc_offset_hours(market: str, now_ts: int) -> int:
        if market == "tw":
            return 8
        if market == "us":
            return -4 if MarketPriceFeed._is_us_dst(now_ts) else -5
        return 0

    @staticmethod
    def _market_local_datetime(market: str, now_ts: int) -> datetime:
        offset_hours = MarketPriceFeed._market_utc_offset_hours(market, now_ts)
        return datetime.fromtimestamp(now_ts, tz=timezone.utc) + timedelta(hours=offset_hours)

    @staticmethod
    def _is_us_dst(now_ts: int) -> bool:
        now_utc = datetime.fromtimestamp(now_ts, tz=timezone.utc)
        year = now_utc.year
        march = datetime(year, 3, 1, tzinfo=timezone.utc)
        first_sunday_offset = (6 - march.weekday()) % 7
        second_sunday = march + timedelta(days=first_sunday_offset + 7)
        november = datetime(year, 11, 1, tzinfo=timezone.utc)
        november_first_sunday = november + timedelta(days=(6 - november.weekday()) % 7)
        dst_start_utc = second_sunday + timedelta(hours=7)
        dst_end_utc = november_first_sunday + timedelta(hours=6)
        return dst_start_utc <= now_utc < dst_end_utc

    def _merge_results(self) -> dict[str, dict[str, float | bool]]:
        return {symbol: self._results.get(symbol, self._empty_item()) for symbol in TICKERS}


class DraggableFrame(QFrame):
    def __init__(self, parent: QWidget | None = None, can_drag=None) -> None:
        super().__init__(parent)
        self._can_drag = can_drag
        self._dragging = False
        self._drag_pos = QPoint()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        can_drag = True if self._can_drag is None else bool(self._can_drag())
        if can_drag and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            win = self.window()
            self._drag_pos = event.globalPosition().toPoint() - win.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._dragging:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()


class MarketTickerWidget(QWidget):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.feed = MarketPriceFeed(self)
        self._is_windows = sys.platform.startswith("win")
        self._movable = True
        self._last_visible_symbols: tuple[str, ...] = ()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.container = DraggableFrame(self, can_drag=lambda: self._movable)
        self.container.setObjectName("container")

        self.status = QLabel("UPDATING")
        self.status.setObjectName("status")

        row0 = QHBoxLayout()
        row0.addWidget(self.status)
        row0.addStretch()

        row1 = QVBoxLayout()
        row1.setSpacing(6)
        self.items: dict[str, dict[str, QWidget | QLabel]] = {}
        for symbol, config in TICKERS.items():
            item = self._create_ticker_item(config["label"])
            self.items[symbol] = item
            row1.addWidget(item["widget"])
        row1.addStretch()

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 10, 12, 10)
        container_layout.setSpacing(6)
        container_layout.addLayout(row0)
        container_layout.addLayout(row1)

        root = QVBoxLayout(self)
        root.setContentsMargins(6 if self._is_windows else 8, 6 if self._is_windows else 8, 6 if self._is_windows else 8, 6 if self._is_windows else 8)
        root.addWidget(self.container)

        self._apply_style()
        self._apply_shadow()
        self._init_tray()

        self.feed.prices_changed.connect(self._on_prices_changed)
        self.feed.status_changed.connect(self._on_status_changed)
        self.feed.start()

        QTimer.singleShot(50, self.move_to_bottom_right)

    def _create_ticker_item(self, label_text: str) -> dict[str, QWidget | QLabel]:
        widget = QWidget(self.container)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        symbol = QLabel(label_text)
        symbol.setObjectName("symbol")

        price = QLabel("--")
        price.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        price.setObjectName("price")
        price.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        change = QLabel("--")
        change.setObjectName("change")
        change.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(symbol)
        layout.addWidget(price)
        layout.addWidget(change)
        layout.addStretch()
        widget.hide()

        return {"widget": widget, "price": price, "change": change}

    def _apply_style(self) -> None:
        style = """
            #container {
                background-color: rgba(18, 18, 22, 195);
                border-radius: 16px;
            }
            QLabel#symbol {
                color: #b8c1d1;
                font-size: 10px;
                min-width: 34px;
            }
            QLabel#price {
                color: #ffffff;
            }
            QLabel#change {
                color: #b8c1d1;
                font-size: 9px;
            }
            QLabel#status {
                color: #7aa2f7;
                font-size: 9px;
            }
        """
        if self._is_windows:
            style = style.replace("border-radius: 16px;", "border: 1px solid #5a5a62;\n                border-radius: 16px;")
        else:
            style = style.replace("border-radius: 16px;", "border: 1px solid rgba(255, 255, 255, 60);\n                border-radius: 18px;")
        self.setStyleSheet(style)

    def _apply_shadow(self) -> None:
        if self._is_windows:
            return
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.container.setGraphicsEffect(shadow)

    def _init_tray(self) -> None:
        self.tray = QSystemTrayIcon(self)

        icon = QIcon.fromTheme("applications-internet")
        if icon.isNull():
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(60, 170, 240))
            icon = QIcon(pixmap)

        self.tray.setIcon(icon)

        self.action_toggle = QAction("Show/Hide", self)
        self.action_pin = QAction("", self)
        self.action_reset = QAction("Move to Bottom Right", self)
        self.action_exit = QAction("Exit", self)

        self.action_toggle.triggered.connect(self.toggle_visibility)
        self.action_pin.triggered.connect(self.toggle_movable)
        self.action_reset.triggered.connect(self.move_to_bottom_right)
        self.action_exit.triggered.connect(self.app.quit)

        self._refresh_action_labels()
        self.tray.setContextMenu(self._create_context_menu())
        self.tray.activated.connect(self._on_tray_clicked)
        self.tray.show()

    def _create_context_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.addAction(self.action_toggle)
        menu.addAction(self.action_pin)
        menu.addAction(self.action_reset)
        menu.addSeparator()
        menu.addAction(self.action_exit)
        return menu

    def _refresh_action_labels(self) -> None:
        self.action_pin.setText("Pin Window" if self._movable else "Unpin Window")

    def toggle_movable(self) -> None:
        self._movable = not self._movable
        self._refresh_action_labels()

    def _on_tray_clicked(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.toggle_visibility()

    def _on_status_changed(self, status: str) -> None:
        self.status.setText(status.upper())
        self._refresh_compact_size()

    def _on_prices_changed(self, prices: dict) -> None:
        visible_symbols: list[str] = []

        for symbol, item in self.items.items():
            data = prices.get(symbol, {})
            price = float(data.get("price", 0.0))
            reference = float(data.get("reference", 0.0))
            visible = bool(data.get("visible", False))
            change = float(data.get("change", 0.0))

            widget = item["widget"]
            price_label = item["price"]
            change_label = item["change"]

            if visible and price > 0:
                price_label.setText(self._format_price(price))
                change_label.setText(self._format_change_pct(change, reference))
                change_label.setStyleSheet(f"color: {self._change_color(change)};")
                widget.show()
                visible_symbols.append(symbol)
            else:
                widget.hide()

        current_visible = tuple(visible_symbols)
        if current_visible != self._last_visible_symbols:
            self._last_visible_symbols = current_visible
            self._refresh_compact_size()
            self.move_to_bottom_right()

    def _refresh_compact_size(self) -> None:
        container_layout = self.container.layout()
        root_layout = self.layout()
        if container_layout is not None:
            container_layout.activate()
        if root_layout is not None:
            root_layout.activate()
        self.container.adjustSize()
        self.adjustSize()
        self.resize(self.sizeHint())

    def toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def contextMenuEvent(self, event) -> None:  # type: ignore[override]
        self._refresh_action_labels()
        menu = self._create_context_menu()
        menu.exec(event.globalPos())

    def move_to_bottom_right(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        self.adjustSize()
        self.move(geo.right() - self.width(), geo.bottom() - self.height())

    @staticmethod
    def _format_price(value: float) -> str:
        return f"{value:,.2f}" if value >= 1000 else f"{value:,.4f}"

    @staticmethod
    def _format_change_pct(change: float, reference: float) -> str:
        if reference <= 0:
            return "--"
        pct = (change / reference) * 100
        sign = "+" if change > 0 else ""
        return f"{sign}{pct:.2f}%"

    @staticmethod
    def _change_color(change: float) -> str:
        if change > 0:
            return UP_COLOR
        if change < 0:
            return DOWN_COLOR
        return FLAT_COLOR


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = MarketTickerWidget(app)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
