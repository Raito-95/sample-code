# crypto_price_ticker

- 路徑: `apps/crypto_price_ticker.py`
- 狀態: `active`

## 工具目的

以常駐小視窗顯示 BTC/ETH 即時價格，支援系統匣操作與自動重連。

## 快速開始

1. 安裝相依套件（至少需 `PySide6`）。
2. 執行：

```bash
python apps/crypto_price_ticker.py
```

3. 透過系統匣可操作：`Show/Hide`、`Pin/Unpin`、`Move to Bottom Right`、`Exit`。

## 功能需求 (FR)

- `FR-1`: 透過 Binance WebSocket 訂閱 `btcusdt@trade`、`ethusdt@trade`。
- `FR-2`: 解析 trade payload，更新 BTC/ETH 最新成交價。
- `FR-3`: 顯示連線狀態（UI 顯示為 `CONNECTING`/`CONNECTED`/`RECONNECTING`）。
- `FR-4`: 斷線後每 5 秒自動重試連線。
- `FR-5`: 價格顯示規則：`>= 1000` 顯示千分位 + 2 位小數，`< 1000` 顯示 4 位小數。
- `FR-6`: 支援系統匣操作（Show/Hide、Pin/Unpin、Move to Bottom Right、Exit）。

## 非功能需求 (NFR)

- `NFR-1`: 視窗保持置頂、可拖曳（Pin 時關閉拖曳）。
- `NFR-2`: UI 保持精簡，優先可讀性。
- `NFR-3`: 網路異常時不崩潰，應維持可恢復狀態。

## 測試

```bash
pytest tests/test_crypto_price_ticker.py -q
```

目前測試覆蓋重點：價格格式化、WebSocket 訊息解析、無效 payload 忽略。

## 已知限制

- 僅支援 Binance 公開即時交易資料流。
- 顯示的是最新成交價，不是 VWAP 或 K 線指標。
- 若地區或網路封鎖 Binance，將無法取得資料。
