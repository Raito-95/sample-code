# Time Complexity and Space Complexity

本文件整理演算法分析常用的時間複雜度與空間複雜度概念。

## Time Complexity

時間複雜度描述輸入規模 `n` 增加時，演算法執行時間的成長趨勢，常用 Big O 表示上界。

### Common Time Complexities

- `O(1)`: Constant time，輸入變大時幾乎不影響步驟數
- `O(log n)`: Logarithmic time，每次縮小問題規模（如二分搜尋）
- `O(n)`: Linear time，步驟與輸入大小成正比
- `O(n log n)`: Linearithmic time，常見於高效排序
- `O(n^2)`: Quadratic time，常見於雙層迴圈
- `O(2^n)`: Exponential time，常見於暴力遞迴

### Time Complexity Examples

- `O(1)`: 陣列以索引取值
- `O(log n)`: 已排序陣列的 binary search
- `O(n)`: linear search
- `O(n log n)`: merge sort（平均）、quick sort（平均）
- `O(n^2)`: bubble sort、selection sort（常見情況）
- `O(2^n)`: 列舉所有子集合

## Space Complexity

空間複雜度描述演算法在輸入規模 `n` 下需要的額外記憶體量。

### Common Space Complexities

- `O(1)`: 僅使用固定額外空間
- `O(n)`: 額外空間與輸入規模成正比
- `O(n^2)`: 需要矩陣等二維結構

### Space Complexity Examples

- `O(1)`: 只使用少量變數的迴圈
- `O(n)`: 建立長度為 `n` 的輔助陣列
- `O(n^2)`: 建立 `n x n` 二維陣列

## Practical Notes

- 複雜度是趨勢分析，不是精確執行時間
- 小資料量時，常數因子可能比 Big O 更關鍵
- 選擇演算法時需同時看時間與空間的取捨
