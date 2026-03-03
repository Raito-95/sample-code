# student_grade_manager

- 路徑: `apps/algorithms_lab/student_grade_manager.py`
- 狀態: `active`

## 工具目的

提供 CLI 學生成績管理流程，支援查詢、新增、刪除與資料持久化。

## 快速開始

1. 進入專案根目錄後執行：

```bash
python apps/algorithms_lab/student_grade_manager.py
```

2. 程式啟動會先嘗試載入 `apps/algorithms_lab/grade2.txt`。
3. 結束流程時會將目前記憶體資料覆寫回 `grade2.txt`。

## 功能需求 (FR)

- `FR-1`: 讀取文字檔成績資料並載入記憶體。
- `FR-2`: 查詢單一學生單科成績。
- `FR-3`: 查詢單一學生全部科目成績。
- `FR-4`: 新增或覆寫學生完整成績資料。
- `FR-5`: 刪除學生成績資料。
- `FR-6`: 結束時將資料寫回檔案。
- `FR-7`: 載入資料時略過空白行與格式錯誤行，並保留有效資料。

## 非功能需求 (NFR)

- `NFR-1`: 對格式錯誤輸入拋出 `ValueError`。
- `NFR-2`: 查無學生或科目時以自訂例外表示（`NoStudentException` / `NoSubjectException`）。
- `NFR-3`: 優先維持簡單、可教學閱讀的實作。

## 資料格式

每行一位學生，格式如下：

```text
student_id subject score [subject score ...]
```

範例：

```text
97531 DS 80 DM 81
```

## 測試

```bash
pytest tests/test_grade_system.py -q
```

目前測試覆蓋重點：輸入格式驗證、非數字分數處理、存檔格式、載入時略過空白/錯誤行。

## 已知限制

- 目前為互動式 CLI，未提供 GUI。
- 未限制分數上下界（只檢查是否為整數）。
- 儲存順序依字典插入順序。
