# Sample Code

## 專案說明

此 repo 目前聚焦三個可維護工具與一組基礎演算法/資料結構範例：

- `apps/system_resource_monitor.py`
- `apps/crypto_price_ticker.py`
- `apps/algorithms_lab/student_grade_manager.py`
- `core/algorithms`
- `core/data_structures`

## 目錄結構

- `apps/`: 可直接執行的工具程式
- `core/`: 可重用、低副作用的核心實作
- `tests/`: 單元測試
- `Doc/`: 教學與設計文件（含 `Doc/Tools` 規格）

## 快速開始

### 1. 建立虛擬環境

```bash
uv venv --python 3.10
```

Windows 啟用：

```bash
.venv\Scripts\activate
```

macOS/Linux 啟用：

```bash
source .venv/bin/activate
```

### 2. 安裝依賴

執行工具：

```bash
uv pip install -r requirements.txt
```

執行測試：

```bash
uv pip install -r requirements-test.txt
```

### 3. 執行應用程式

```bash
uv run --python 3.10 --with-requirements requirements.txt python apps/system_resource_monitor.py
uv run --python 3.10 --with-requirements requirements.txt python apps/crypto_price_ticker.py
uv run --python 3.10 --with-requirements requirements.txt python apps/algorithms_lab/student_grade_manager.py
```

### 4. 執行測試

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/ --cov=. --cov-report=term --cov-report=html
```

## 文件索引

- 工具規格與教學：`Doc/Tools/`
- 測試流程：`TESTING.md`
- 貢獻流程：`CONTRIBUTING.md`

## 維護原則

- `apps/` 可依賴 GUI、網路與系統資源 API。
- `core/` 應保持可測試、可重用。
- 修改行為時請同步更新 `README.md`、`TESTING.md`、`CONTRIBUTING.md`、`Doc/Tools/*.md`。
