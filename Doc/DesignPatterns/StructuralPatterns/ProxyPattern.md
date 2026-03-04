# 代理模式（Proxy Pattern）

## 概觀

代理模式是一種結構型設計模式，提供「代理物件」代表真實物件對外服務。代理可在轉發前後加入權限控制、延遲載入、記錄等邏輯。

## Python 實作

可建立 `Proxy` 與 `RealSubject` 實作相同介面，讓客戶端透過代理存取真實物件。

### 程式範例
```python
class Subject:
    """ Define the common interface for RealSubject and Proxy so that a Proxy can be used anywhere a RealSubject is expected. """
    def request(self):
        pass

class RealSubject(Subject):
    """ Define the real object that the proxy represents. """
    def request(self):
        return "RealSubject: Handling request."

class Proxy(Subject):
    """ The Proxy maintains a reference to an object of the RealSubject class and controls access to it. """
    def __init__(self, real_subject):
        self._real_subject = real_subject

    def request(self):
        if self.check_access():
            response = self._real_subject.request()
            self.log_access()
            return f"Proxy: Log start -> {response} -> Log end"
        else:
            return "Proxy: Access denied."

    def check_access(self):
        """ Simulate the access control. """
        # Implement the condition checks for accessing the real subject.
        return True  # Access is granted

    def log_access(self):
        """ Log the access details. """
        print("Proxy: Logging access to the real subject.")

# Using the Proxy Pattern
real_subject = RealSubject()
proxy = Proxy(real_subject)
print(proxy.request())  # Output: Proxy: Log start -> RealSubject: Handling request. -> Log end
```

### 範例說明

`Proxy` 在轉發請求前先做存取檢查，並於完成後記錄存取行為。

## 小結

代理模式能在不改動核心物件的前提下附加控制邏輯，適合權限、快取與監控等場景。
