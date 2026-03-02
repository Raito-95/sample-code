# Testing Guide

## 目的

本文件說明本 repo 的測試執行方式，基準為 `uv + pytest`。

## 前置需求

- 安裝 `uv`
- 不需手動安裝 Python（由 `uv` 管理）

## 安裝測試依賴

```bash
uv venv --python 3.10
uv pip install -r requirements-test.txt
```

## 執行全部測試

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/ --cov=. --cov-report=term --cov-report=html
```

輸出：

- 終端機 coverage 摘要
- `htmlcov/index.html`

## 執行指定測試

單一檔案：

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/test_system_resource_monitor.py -q
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/test_crypto_price_ticker.py -q
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/test_grade_system.py -q
```

單一測試案例：

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/test_search_algorithms.py::test_binary_search -q
```

## CI 對齊

GitHub Actions 會在 `push/pull_request` 到 `main` 時執行相同測試流程。

## 測試撰寫原則

- 檔名使用 `test_*.py`
- 優先撰寫 deterministic unit tests
- 盡量避免依賴即時網路/硬體狀態
