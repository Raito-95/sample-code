# 單例模式（Singleton Pattern）

## 概觀

單例模式可確保某個類別在系統中只有一個實例，並提供全域存取點，常用於設定管理與共享資源。

## Python 實作

常見做法是在 `__new__` 中控管實例建立，確保後續建立動作都回傳同一個物件。

### 程式範例

```python
class Singleton:
    _instance = None  # Static variable that stores the unique instance of the class

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

# Testing the Singleton Pattern
instance1 = Singleton()
instance2 = Singleton()
print(instance1 is instance2)  # Outputs True, proving that instance1 and instance2 are the same instance
```

### 範例說明

執行結果會得到 `True`，代表 `instance1` 與 `instance2` 指向同一個物件。

## 小結

單例模式可統一共享狀態與資源，但也要注意過度使用可能增加測試與維護難度。
