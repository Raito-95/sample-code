# 測試說明

本專案包含各類資料結構與演算法模組，測試以 `pytest` 撰寫，整合至 GitHub Actions 執行自動化測試與測試覆蓋率分析（透過 `pytest-cov`）。

---

## 前置條件

只需安裝 `uv`，不需要另外手動安裝 Python。

---

## 安裝測試相依套件

如需建立本地 `.venv`，可先執行：

```bash
uv venv --python 3.10
```

再安裝測試相依套件：

```bash
uv pip install -r requirements-test.txt
```

`requirements-test.txt` 應包含：

```
pytest
pytest-cov
```

---

## 執行測試（本地環境）

建議直接使用 uv 執行（由 uv 管理 Python 與套件）：

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/ --cov=. --cov-report=term --cov-report=html
```

* 終端機將顯示測試覆蓋率摘要
* HTML 覆蓋率報告將產出於 `htmlcov/index.html`

---

## 測試工具說明

| 工具               | 功能         |
| ---------------- | ---------- |
| `pytest`         | 單元測試框架     |
| `pytest-cov`     | 顯示覆蓋率報告    |
| `GitHub Actions` | 自動化測試與報告上傳 |

---

## 測試對應模組一覽

| 測試檔案                                    | 對應模組               | 測試重點                           |
| --------------------------------------- | ------------------ | ------------------------------ |
| test\_sorting\_algorithms\_recursion.py | sorting 演算法        | bubble, merge, quick sort      |
| test\_search\_algorithms.py             | search 演算法         | linear, binary                 |
| test\_list\_analysis\_functions.py      | list 處理函式          | is\_sorted, find\_max          |
| test\_fibonacci\_methods.py             | Fibonacci          | 遞迴、迴圈、例外處理                     |
| test\_singly\_linked\_list.py           | Singly Linked List | append、delete、search、reverse   |
| test\_doubly\_linked\_list.py           | Doubly Linked List | append、delete、正反向 traversal    |
| test\_list\_based\_stack.py             | Stack              | push、pop、peek、size、is\_empty   |
| test\_deque\_based\_queue.py            | Queue              | enqueue、dequeue、peek 等         |
| test\_binary\_tree.py                   | Binary Tree        | 各種 traversal                   |
| test\_binary\_search\_tree.py           | Binary Search Tree | insert、search、delete、traversal |

---

## GitHub Actions 設定摘要

* 設定檔位置：`.github/workflows/python-ci.yml`
* 觸發條件：push 或 PR 到 `main` 分支
* 流程概要：

  1. 安裝 uv
  2. 由 uv 自動提供 Python 3.10 與 `requirements-test.txt` 中的套件
  3. 執行 `pytest` 並產生覆蓋率報告
  4. 上傳 HTML 覆蓋率報告至 Artifacts

---

## 測試輸出位置

| 類型         | 路徑                   | 備註           |
| ---------- | -------------------- | ------------ |
| 終端機覆蓋率統計   | 標準輸出                 | pytest 執行時顯示 |
| HTML 覆蓋率報告 | `htmlcov/index.html` | 可用瀏覽器查看      |

---

## 補充

* 所有測試檔請遵循 `test_*.py` 命名格式
* 建議每個模組對應獨立測試檔，便於維護與擴充
* 如需其他測試報告格式，可整合 `pytest-html` 或 `junit-xml`
