import json
import sys

from PySide6.QtCore import QObject, QPoint, QTimer, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QColor, QFont, QGuiApplication, QIcon, QPixmap
from PySide6.QtNetwork import QAbstractSocket
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

BINANCE_STREAM = (
    "wss://stream.binance.com:9443/stream?"
    "streams=btcusdt@trade/ethusdt@trade"
)


class PriceFeed(QObject):
    prices_changed = Signal(float, float)
    status_changed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._last_btc: float | None = None
        self._last_eth: float | None = None

        self.ws = QWebSocket()
        self.ws.connected.connect(self._on_connected)
        self.ws.disconnected.connect(self._on_disconnected)
        self.ws.textMessageReceived.connect(self._on_message)

        self.retry_timer = QTimer(self)
        self.retry_timer.setInterval(5000)
        self.retry_timer.timeout.connect(self.connect)

    def connect(self) -> None:
        if self.ws.state() in (
            QAbstractSocket.SocketState.ConnectedState,
            QAbstractSocket.SocketState.ConnectingState,
        ):
            return
        self.status_changed.emit("connecting")
        self.ws.open(QUrl(BINANCE_STREAM))

    def _on_connected(self) -> None:
        self.status_changed.emit("connected")
        self.retry_timer.stop()

    def _on_disconnected(self) -> None:
        self.status_changed.emit("reconnecting")
        if not self.retry_timer.isActive():
            self.retry_timer.start()

    def _on_message(self, msg: str) -> None:
        try:
            payload = json.loads(msg)
            stream = payload.get("stream", "")
            data = payload.get("data", {})
            price = float(data.get("p", ""))
        except (TypeError, ValueError, json.JSONDecodeError):
            return

        if stream.startswith("btcusdt"):
            self._last_btc = price
        elif stream.startswith("ethusdt"):
            self._last_eth = price
        else:
            return

        self.prices_changed.emit(self._last_btc or 0.0, self._last_eth or 0.0)


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


class TickerWidget(QWidget):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.feed = PriceFeed(self)
        self._is_windows = sys.platform.startswith("win")
        self._movable = True

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        if not self._is_windows:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.container = DraggableFrame(self, can_drag=lambda: self._movable)
        self.container.setObjectName("container")

        self.status = QLabel("CONNECTING")
        self.status.setObjectName("status")

        self.btc_symbol = QLabel("BTC")
        self.eth_symbol = QLabel("ETH")
        for label in (self.btc_symbol, self.eth_symbol):
            label.setObjectName("symbol")

        self.btc_price = QLabel("--")
        self.eth_price = QLabel("--")
        price_font = QFont("Consolas", 13, QFont.Weight.Bold)
        for label in (self.btc_price, self.eth_price):
            label.setFont(price_font)
            label.setObjectName("price")
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row0 = QHBoxLayout()
        row0.addWidget(self.status)
        row0.addStretch()

        row1 = QHBoxLayout()
        row1.addWidget(self.btc_symbol)
        row1.addStretch()
        row1.addWidget(self.btc_price)

        row2 = QHBoxLayout()
        row2.addWidget(self.eth_symbol)
        row2.addStretch()
        row2.addWidget(self.eth_price)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 10, 12, 10)
        container_layout.setSpacing(4)
        container_layout.addLayout(row0)
        container_layout.addLayout(row1)
        container_layout.addLayout(row2)

        root = QVBoxLayout(self)
        if self._is_windows:
            root.setContentsMargins(0, 0, 0, 0)
        else:
            root.setContentsMargins(8, 8, 8, 8)
        root.addWidget(self.container)

        self._apply_style()
        self._apply_shadow()
        self._init_tray()

        self.feed.prices_changed.connect(self._on_prices_changed)
        self.feed.status_changed.connect(self._on_status_changed)
        self.feed.connect()

        QTimer.singleShot(50, self.move_to_bottom_right)

    def _apply_style(self) -> None:
        if self._is_windows:
            self.setStyleSheet(
                """
                #container {
                    background-color: #121216;
                    border: 1px solid #5a5a62;
                    border-radius: 10px;
                }
                QLabel#symbol {
                    color: #b8c1d1;
                    font-size: 10px;
                    min-width: 34px;
                }
                QLabel#price {
                    color: #ffffff;
                }
                QLabel#status {
                    color: #7aa2f7;
                    font-size: 9px;
                }
                """
            )
            return

        self.setStyleSheet(
            """
            #container {
                background-color: rgba(18, 18, 22, 220);
                border: 1px solid rgba(255, 255, 255, 60);
                border-radius: 12px;
            }
            QLabel#symbol {
                color: #b8c1d1;
                font-size: 10px;
                min-width: 34px;
            }
            QLabel#price {
                color: #ffffff;
            }
            QLabel#status {
                color: #7aa2f7;
                font-size: 9px;
            }
            """
        )

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

    def _on_prices_changed(self, btc: float, eth: float) -> None:
        if btc > 0:
            self.btc_price.setText(self._format_price(btc))
        if eth > 0:
            self.eth_price.setText(self._format_price(eth))

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


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = TickerWidget(app)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
