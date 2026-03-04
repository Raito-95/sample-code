# Tools 文件索引

## 目的

`Doc/Tools/` 用於維護 `apps/` 工具的使用說明與需求規格。

## 內容清單

- `crypto_price_ticker.md`：對應 `apps/crypto_price_ticker.py`
- `system_resource_monitor.md`：對應 `apps/system_resource_monitor.py`
- `student_grade_manager.md`：對應 `apps/algorithms_lab/student_grade_manager.py`

## 建議閱讀順序

1. 先看本索引定位目標工具。
2. 進入工具文件閱讀快速開始。
3. 若需確認行為，查看 FR/NFR 與測試章節。

## 維護規則

1. 每個工具維持一份對應文件（檔名對應模組名）。
2. 工具文件至少包含：目的、快速開始、FR、NFR、測試、已知限制。
3. 程式行為或測試變更時，文件需同次提交更新。
4. 本檔只保留導覽，不重複工具細節。
