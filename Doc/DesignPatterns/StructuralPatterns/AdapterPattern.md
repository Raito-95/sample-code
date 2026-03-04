# 轉接器模式（Adapter Pattern）

## 概觀

轉接器模式是一種結構型設計模式，可讓介面不相容的類別彼此協作。它透過中介層把既有介面轉成客戶端期望的介面。

## Python 實作

常見做法是建立 `Adapter` 包裝既有物件，並在 `Adapter` 內轉換資料或呼叫方式。

### 程式範例
```python
class Target:
    """ The Target defines the domain-specific interface used by the client code. """
    def request(self):
        return "Target: The default target's behavior."

class Adaptee:
    """ The Adaptee contains some useful behavior, but its interface is incompatible
    with the existing client code. The Adaptee needs some adaptation before the client code can use it. """
    def specific_request(self):
        return ".eetpadA eht fo roivaheb laicepS"

class Adapter(Target):
    """ The Adapter makes the Adaptee's interface compatible with the Target's interface via inheritance. """
    def __init__(self, adaptee):
        self._adaptee = adaptee

    def request(self):
        return f"Adapter: (TRANSLATED) {self._adaptee.specific_request()[::-1]}"

# Using the Adapter Pattern
adaptee = Adaptee()
print(f"Adaptee: {adaptee.specific_request()}")  # Adaptee's existing behavior doesn't match the client's expectations.

adapter = Adapter(adaptee)
print(adapter.request())  # Output: Adapter: (TRANSLATED) Special behavior of the Adaptee.
```

### 範例說明

`Adapter` 反轉 `Adaptee` 回傳字串後，讓客戶端能以 `Target` 介面取得可用結果。

## 小結

轉接器模式特別適合整合舊系統或第三方元件，可在不修改原始碼下完成介面相容。
