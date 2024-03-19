# 清理 gh-pages 分支歷史

## 目的
從 `gh-pages` 分支中刪除除最新提交外的所有歷史記錄，使該分支僅包含最新的一次提交。

## 步驟

### 1. 切換到 `gh-pages` 分支並創建臨時分支
首先，切換到您的 `gh-pages` 分支，然後創建一個新的臨時分支指向當前的最新提交：

```bash
git checkout gh-pages
git checkout -b temp-branch
```

### 2. 刪除原有的 gh-pages 分支
刪除本地的 gh-pages 分支：

```bash
git branch -D gh-pages
```

### 3. 創建一個新的 gh-pages 分支
使用 --orphan 選項創建一個新的 gh-pages 分支，這樣可以開始一個沒有任何歷史記錄的新分支：

```bash
git checkout --orphan gh-pages
git commit -m "Retain only the latest commit"
```

這個提交將成為新的 gh-pages 分支上的第一個提交，且分支中不會包含任何其他歷史記錄。

### 4. 強制推送更改到遠端
將本地更改強制推送到 GitHub 上的 gh-pages 分支，以更新遠端分支的歷史：

```bash
git push origin gh-pages --force
```

### 注意事項
數據備份：在進行上述操作之前，請確保已備份所有必要的數據。此過程將徹底刪除 gh-pages 分支的舊歷史記錄。
風險：強制推送 (--force) 會重寫遠端分支的歷史。這種操作是破壞性的，應謹慎使用。
通過以上步驟，您可以有效地清理 gh-pages 分支的歷史記錄，僅保留最新的提交。