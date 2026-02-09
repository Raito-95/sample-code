# 測試說明

本專案包含各類資料結構與演算法模組，測試以 `pytest` 撰寫，整合至 GitHub Actions 執行自動化測試與測試覆蓋率分析（透過 `pytest-cov`）。

---

## 安裝測試相依套件

請使用獨立的測試依賴檔案（若使用 uv 管理環境，先建立 venv）：

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

再安裝測試依賴：

```bash
uv pip install -r requirements-test.txt
```

> 補充：`uv init` 主要用於初始化新專案（建立 `pyproject.toml`/`uv.lock`）。
> 本專案維持 `requirements-test.txt`，因此用 `uv pip install -r ...` 即可。

`requirements-test.txt` 應包含：

```
pytest
pytest-cov
```

---

## 執行測試（本地環境）

```bash
pytest --cov=. --cov-report=term --cov-report=html
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

  1. 安裝 Python 3.10
  2. 安裝 `requirements-test.txt` 中的套件
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
