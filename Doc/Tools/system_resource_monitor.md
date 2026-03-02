# system_resource_monitor

- 路徑: `apps/system_resource_monitor.py`
- 狀態: `active`

## 工具目的

提供常駐桌面的輕量系統資源監控，採純文字卡片顯示，降低視覺噪音。

## 顯示內容

- CPU: 使用率、品牌
- Memory: 使用率與已用/總量 (GB)
- GPU: 使用率、溫度、VRAM（偵測到才顯示）
- Disk: 每個掛載點/磁碟分區使用率與已用/總量 (GB)

## 功能需求 (FR)

- `FR-1`: CPU 每秒更新。
- `FR-2`: Memory 每 2 秒更新。
- `FR-3`: Disk 每 15 秒更新（避免高頻 I/O）。
- `FR-4`: 使用 NVML 讀取 NVIDIA GPU 資訊。
- `FR-5`: 若啟動時 GPU 初始化失敗，需每 10 秒自動重試偵測。
- `FR-6`: 偵測到 GPU 後自動顯示 GPU 區塊並開始更新。
- `FR-7`: 支援系統匣操作（Show/Hide、Pin/Unpin、Move to Bottom Right、Exit）。

## 非功能需求 (NFR)

- `NFR-1`: 不使用趨勢圖，僅保留文字資訊。
- `NFR-2`: 視窗寬度可依內容自動壓縮。
- `NFR-3`: 沒有 GPU 或 NVML 不可用時，程式仍可運作。

## 已知限制

- GPU 監控目前只支援 NVIDIA（`pynvml`）。
- Disk 顯示依作業系統掛載點命名，平台間格式可能不同。
