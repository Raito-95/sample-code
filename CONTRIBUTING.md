# Contributing

## 變更範圍

- `core/`: 放可重用邏輯，避免副作用
- `apps/`: 放可執行工具，可依賴 GUI/網路/系統 API
- `tests/`: 驗證行為，避免 fragile 測試

## PR 基本規則

1. 從 `main` 開分支
2. 一個 PR 聚焦一件事
3. PR 需附測試結果

## 必做檢查

提交前請至少執行：

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/ --cov=. --cov-report=term --cov-report=html
```

若是局部修改，請再附上目標測試：

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/test_system_resource_monitor.py -q
```

## 文件同步

當行為或命令改變時，請同步更新：

- `README.md`
- `TESTING.md`
- `Doc/Tools/*.md`

## 命名與風格

- 使用描述性檔名與函式命名
- 盡量保持模組單一職責
- 避免在同一 PR 夾雜無關重構
