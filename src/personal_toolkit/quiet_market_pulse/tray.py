from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from time import monotonic

from personal_toolkit.quiet_market_pulse.config import DEFAULT_CONFIG_PATH, PROJECT_ROOT, load_config
from personal_toolkit.quiet_market_pulse.formatting import format_percent, format_price
from personal_toolkit.quiet_market_pulse.models import InstrumentConfig, Quote
from personal_toolkit.quiet_market_pulse.pulse import is_visible
from personal_toolkit.quiet_market_pulse.sources import QuoteUnavailable, fetch_quote


LOG_PATH = PROJECT_ROOT / "logs" / "quiet_market_pulse.log"


class PulseState:
    def __init__(
        self,
        stale_after_seconds: float = 180,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.last_quotes: dict[tuple[str, str], tuple[Quote, float]] = {}
        self.stale_after_seconds = stale_after_seconds
        self.clock = clock

    def update(self, instruments: tuple[InstrumentConfig, ...]) -> list[Quote]:
        if not instruments:
            return []

        visible: list[Quote] = []
        with ThreadPoolExecutor(
            max_workers=min(4, len(instruments)),
            thread_name_prefix="quote-source",
        ) as fetch_executor:
            pending_quotes = [
                (instrument, fetch_executor.submit(fetch_quote, instrument))
                for instrument in instruments
            ]
            for instrument, future in pending_quotes:
                cache_key = (instrument.source, instrument.symbol)
                try:
                    quote = future.result()
                    self.last_quotes[cache_key] = (quote, self.clock())
                except QuoteUnavailable:
                    cached = self.last_quotes.get(cache_key)
                    if cached is None:
                        continue
                    quote, fetched_at = cached
                    if self.clock() - fetched_at > self.stale_after_seconds:
                        self.last_quotes.pop(cache_key, None)
                        continue

                if is_visible(instrument, quote):
                    visible.append(quote)
        return visible


def main() -> int:
    try:
        from PySide6.QtCore import QPoint, Qt, QTimer
        from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
        from PySide6.QtWidgets import (
            QApplication,
            QFrame,
            QGraphicsDropShadowEffect,
            QHBoxLayout,
            QLabel,
            QMenu,
            QSizePolicy,
            QSystemTrayIcon,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:
        raise SystemExit("PySide6 is required to run the UI") from exc

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO)

    config = load_config(DEFAULT_CONFIG_PATH)
    state = PulseState(stale_after_seconds=max(180, config.refresh_seconds * 3))

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = QWidget()
    window.setWindowTitle("Quiet Market Pulse")
    window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    window.setMinimumWidth(260)

    panel = QFrame()
    panel.setObjectName("pulsePanel")
    panel.setStyleSheet(
        """
        QFrame#pulsePanel {
            background: rgba(17, 24, 39, 236);
            border: 1px solid rgba(148, 163, 184, 92);
            border-radius: 10px;
        }
        QLabel {
            color: #f9fafb;
            font-family: Segoe UI;
            font-size: 12px;
            letter-spacing: 0px;
        }
        QLabel#nameLabel {
            color: #e5e7eb;
            font-weight: 600;
        }
        QLabel#priceLabel {
            color: #f8fafc;
            font-weight: 600;
        }
        QLabel#emptyLabel {
            color: #94a3b8;
            padding-top: 2px;
        }
        """
    )

    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(22)
    shadow.setOffset(0, 8)
    shadow.setColor(QColor(0, 0, 0, 110))
    panel.setGraphicsEffect(shadow)

    layout = QVBoxLayout(window)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.addWidget(panel)

    panel_layout = QVBoxLayout(panel)
    panel_layout.setContentsMargins(12, 10, 12, 10)
    panel_layout.setSpacing(6)

    rows_layout = QVBoxLayout()
    rows_layout.setContentsMargins(0, 0, 0, 0)
    rows_layout.setSpacing(4)
    panel_layout.addLayout(rows_layout)

    drag_origin: QPoint | None = None
    user_moved = False

    def plain_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setTextFormat(Qt.TextFormat.PlainText)
        return label

    def position_bottom_right() -> None:
        screen = app.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        margin = 18
        window.move(
            available.right() - window.width() - margin,
            available.bottom() - window.height() - margin,
        )

    def mouse_press(event) -> None:  # type: ignore[no-untyped-def]
        nonlocal drag_origin
        if event.button() == Qt.MouseButton.LeftButton:
            drag_origin = event.globalPosition().toPoint() - window.frameGeometry().topLeft()

    def mouse_move(event) -> None:  # type: ignore[no-untyped-def]
        nonlocal user_moved
        if drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            user_moved = True
            window.move(event.globalPosition().toPoint() - drag_origin)

    def mouse_release(event) -> None:  # type: ignore[no-untyped-def]
        nonlocal drag_origin
        drag_origin = None

    window.mousePressEvent = mouse_press
    window.mouseMoveEvent = mouse_move
    window.mouseReleaseEvent = mouse_release

    def clear_rows() -> None:
        while rows_layout.count():
            item = rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def percent_color(quote: Quote) -> str:
        if quote.change_percent is None:
            return "#94a3b8"
        if quote.change_percent > 0:
            return "#22c55e"
        if quote.change_percent < 0:
            return "#f43f5e"
        return "#94a3b8"

    def add_quote_row(quote: Quote) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        name = plain_label(quote.label)
        name.setObjectName("nameLabel")
        name.setMinimumWidth(44)

        price = plain_label(format_price(quote.price))
        price.setObjectName("priceLabel")
        price.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        percent = plain_label(format_percent(quote.change_percent))
        percent.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        percent.setMinimumWidth(58)
        percent.setStyleSheet(f"color: {percent_color(quote)}; font-weight: 700;")

        row_layout.addWidget(name)
        row_layout.addWidget(price)
        row_layout.addWidget(percent)
        rows_layout.addWidget(row)

    def render_quotes(quotes: list[Quote]) -> None:
        clear_rows()
        if not quotes:
            empty_text = (
                "Data unavailable"
                if any(instrument.show_when_closed for instrument in config.instruments)
                else "Markets closed"
            )
            empty = plain_label(empty_text)
            empty.setObjectName("emptyLabel")
            rows_layout.addWidget(empty)
        for quote in quotes:
            add_quote_row(quote)

    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="market-pulse")
    refresh_future: Future[list[Quote]] | None = None

    def refresh() -> None:
        nonlocal refresh_future
        if refresh_future is not None:
            return
        refresh_future = executor.submit(state.update, config.instruments)

    def apply_refresh_result() -> None:
        nonlocal refresh_future
        if refresh_future is None or not refresh_future.done():
            return
        completed_future = refresh_future
        refresh_future = None
        try:
            quotes = completed_future.result()
            render_quotes(quotes)
            window.adjustSize()
            if not user_moved:
                position_bottom_right()
        except Exception:
            logging.exception("refresh failed")

    icon_pixmap = QPixmap(32, 32)
    icon_pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(icon_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#111827"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, 28, 28, 6, 6)
    painter.setBrush(QColor("#22c55e"))
    painter.drawRect(8, 17, 3, 7)
    painter.drawRect(14, 11, 3, 13)
    painter.drawRect(20, 7, 3, 17)
    painter.end()

    tray = QSystemTrayIcon(QIcon(icon_pixmap), app)
    menu = QMenu()

    show_hide = QAction("Show/Hide", menu)

    def toggle_window() -> None:
        window.hide() if window.isVisible() else window.show()

    show_hide.triggered.connect(toggle_window)
    menu.addAction(show_hide)

    exit_action = QAction("Exit", menu)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    tray.setContextMenu(menu)
    tray.activated.connect(lambda _reason: toggle_window())
    tray.show()

    window.show()
    position_bottom_right()
    refresh()

    refresh_timer = QTimer()
    refresh_timer.timeout.connect(refresh)
    refresh_timer.start(config.refresh_seconds * 1000)

    result_timer = QTimer()
    result_timer.timeout.connect(apply_refresh_result)
    result_timer.start(100)

    app.aboutToQuit.connect(lambda: executor.shutdown(wait=False, cancel_futures=True))

    return app.exec()
