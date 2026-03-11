# market_index_ticker

- 路徑: `apps/market_index_ticker.py`
- 狀態: `active`

## 工具目的

以常駐小視窗顯示 BTC、美股三大指數與台股加權指數，且僅在市場開盤時顯示對應指數。

## 快速開始

1. 安裝相依套件（至少需 `PySide6`）。
2. 執行：

```bash
uv run --python 3.10 --with-requirements requirements.txt python apps/market_index_ticker.py
```

3. 透過系統匣可操作：`Show/Hide`、`Pin/Unpin`、`Move to Bottom Right`、`Exit`。

## 功能需求 (FR)

- `FR-1`: 透過 Yahoo Finance quote API 抓取 `BTC-USD`、`^DJI`、`^GSPC`、`^IXIC`、`^TWII`。
- `FR-2`: BTC 因 24/7 交易，價格有效時持續顯示。
- `FR-3`: 美股三大指數與台股加權指數僅在 `marketState=REGULAR` 時顯示。
- `FR-4`: 未開盤、休市、缺值時，對應指數整段隱藏，不保留空白欄位。
- `FR-5`: 價格顯示規則：`>= 1000` 顯示千分位 + 2 位小數，`< 1000` 顯示 4 位小數。
- `FR-6`: 支援系統匣操作（Show/Hide、Pin/Unpin、Move to Bottom Right、Exit）。

## 非功能需求 (NFR)

- `NFR-1`: 視窗保持置頂、可拖曳（Pin 時關閉拖曳）。
- `NFR-2`: UI 保持精簡，優先可讀性。
- `NFR-3`: 網路異常時不崩潰，下次輪詢可自動恢復。

## 測試

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/test_market_index_ticker.py -q
```

目前測試覆蓋重點：價格格式化、開盤顯示規則、關閉市場隱藏。

## 已知限制

- 依賴 Yahoo Finance quote API，若來源異常或被限制，資料會暫時無法更新。
- 開盤判斷依 `marketState`，若上游欄位定義變動，需同步調整。
