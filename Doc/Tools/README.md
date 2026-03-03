# Tools 文件索引

這個資料夾是 `apps/` 工具的需求與教學維護基準。

## 文件規則

1. 每個工具一份文件，檔名對應 Python 模組。
2. 內容至少包含：工具目的、快速開始、功能需求（FR）、非功能需求（NFR）、測試、已知限制。
3. 程式行為改動後，文件需同 PR 一起更新。

## 目前維護工具

- `apps/crypto_price_ticker.py` -> `crypto_price_ticker.md`
- `apps/system_resource_monitor.py` -> `system_resource_monitor.md`
- `apps/algorithms_lab/student_grade_manager.py` -> `student_grade_manager.md`

## 建議維護流程

1. 先更新程式與測試。
2. 再同步更新 `Doc/Tools/*.md` 的 FR/NFR 與操作說明。
3. 最後以對應測試檔確認文件描述沒有偏差。
