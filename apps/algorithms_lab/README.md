# Student Grade Manager

`student_grade_manager.py` 是演算法實驗區的 CLI 範例，提供學生成績資料管理。

## 主要功能

- 查詢單一科目成績
- 查詢該生全部成績
- 新增/覆寫學生成績
- 刪除學生成績
- 讀檔載入與存檔
- 載入時略過空白行與無效資料行

## 執行方式

```bash
uv run --python 3.10 --with-requirements requirements.txt python apps/algorithms_lab/student_grade_manager.py
```

## 資料來源

- 預設檔案：`apps/algorithms_lab/grade2.txt`
- 啟動時載入，結束流程時覆寫回檔案

## 資料格式

每行格式：

```text
97501 DS 80 DM 76 LA 63
```

說明：

- 第 1 欄：學號
- 其餘欄位：`科目 分數` 成對出現
- 分數需為整數

## 測試

```bash
uv run --python 3.10 --with-requirements requirements-test.txt pytest tests/test_grade_system.py -q
```
