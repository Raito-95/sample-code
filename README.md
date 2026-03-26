# Sample Code

這是一個以 Python 為主的練習與教學型專案，內容分成三個主要區塊：

- `core/`：可重用的演算法與資料結構實作
- `apps/`：可直接執行的桌面工具與 CLI 範例
- `Doc/`：主題式教學、工具說明與補充文件

## 專案結構

- `apps/system_resource_monitor.py`
  顯示 CPU、記憶體、磁碟與 GPU 使用狀態的桌面監看工具。
- `apps/market_index_ticker.py`
  顯示 BTC 與主要市場指數的桌面 ticker。
- `apps/algorithms_lab/student_grade_manager.py`
  學生成績管理 CLI，示範檔案存取與資料驗證流程。
- `core/algorithms/`
  搜尋、排序、遞迴與清單分析等基礎演算法。
- `core/data_structures/`
  Stack、Queue、Linked List、Tree、BST 等資料結構。
- `tests/`
  以 `pytest` 撰寫的單元測試。
- `Doc/`
  工具文件、Python OOP、複雜度與設計模式整理。

## 快速開始

### 1. 建立虛擬環境

```bash
uv venv --python 3.10
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 2. 安裝依賴

執行工具需要：

```bash
uv pip install -r requirements.txt
```

執行測試需要：

```bash
uv pip install -r requirements-test.txt
```

### 3. 執行範例工具

```bash
uv run --python 3.10 --with-requirements requirements.txt python apps/system_resource_monitor.py
uv run --python 3.10 --with-requirements requirements.txt python apps/market_index_ticker.py
uv run --python 3.10 --with-requirements requirements.txt python apps/algorithms_lab/student_grade_manager.py
```

### 4. 執行測試

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/ --cov=. --cov-report=term --cov-report=html
```

## 文件導覽

- 工具說明：`Doc/Tools/`
- 文件入口：`Doc/README.md`
- 測試指南：`TESTING.md`
- 協作規範：`CONTRIBUTING.md`

## 維護原則

- `core/` 優先放純邏輯、低副作用、可測試的程式碼。
- `apps/` 可以依賴 GUI、網路或系統 API。
- 行為、命令或檔案位置有變動時，請同步更新 `README.md`、`TESTING.md`、`CONTRIBUTING.md` 與相關 `Doc/Tools/*.md`。
