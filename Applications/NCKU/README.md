# 使用者操作手冊

## 1. 前置準備
在開始使用本程式之前，請確保您的系統中已安裝以下軟體和套件：

- Python 3.10 或更高版本
- Chrome 瀏覽器

## 2. 安裝套件
使用提供的 `setup.py` 和 `requirements.txt` 文件來安裝所需的 Python 套件。在程式所在的目錄下，執行以下命令：

```bash
pip install .
```

## 3. 設定檔案
程式需要一個名為 credentials.json 的配置檔案，用於存儲登入資訊和其他設定。請在程式所在的目錄下創建此檔案，並填入以下內容：

```json
{
    "psn_code": "您的使用者帳號",
    "password": "您的密碼",
    "line_notify_token": "您的LINE Notify令牌",
    "sign_in_minute_start": 0,
    "sign_in_minute_end": 20
}
```
 - psn_code: 您的使用者帳號。
 - password: 您的密碼。
 - line_notify_token: 您的 LINE Notify 令牌，用於發送通知消息。您可以從 [LINE Notify 網站](https://notify-bot.line.me/) 獲取令牌。
 - sign_in_minute_start: 允許的簽到時間範圍的開始分鐘數（0 到 59 之間）。
 - sign_in_minute_end: 允許的簽到時間範圍的結束分鐘數（必須大於 sign_in_minute_start 且不超過 60）。

## 4. 運行程式
確保所有設定都已完成後，您可以通過以下命令來運行程式：

```bash
python AutomatedWorkClock.py
```
程式將自動根據當前時間和設定的工作日程表進行簽到和簽退操作，並通過 LINE 發送相應的通知消息。

## 5. 注意事項
- 確保您的系統時間設定正確，以便程式能夠準確地進行簽到和簽退操作。
- 程式將在後台運行，不會打開瀏覽器視窗。您可以查看程式輸出或 LINE 通知來確認操作狀態。
- 如果需要停止程式，您可以使用終端機的中斷命令（如 Ctrl+C）來終止執行。

## 6. 維護與更新
- 定期檢查程式依賴的套件是否有更新，並及時進行升級。
- 根據需要調整 credentials.json 中的配置設定。
- 如果遇到任何問題或錯誤，請檢查程式的日誌記錄並根據錯誤訊息進行排查。