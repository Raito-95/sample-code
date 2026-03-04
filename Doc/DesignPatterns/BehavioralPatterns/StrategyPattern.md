# 策略模式（Strategy Pattern）

## 概觀

策略模式是一種行為型設計模式，將一組可互換的演算法封裝成不同策略，讓系統可以在執行期選擇要使用哪一種演算法。

## Python 實作

通常會定義共同策略介面、多個具體策略，以及一個 `Context` 來持有並使用策略。

### 程式範例
```python
class Strategy:
    """ Define an interface common to all supported algorithms. """
    def do_algorithm(self, data):
        pass

class ConcreteStrategyA(Strategy):
    """ Implement the algorithm using the Strategy interface. """
    def do_algorithm(self, data):
        return sorted(data)

class ConcreteStrategyB(Strategy):
    """ Implement the algorithm using the Strategy interface. """
    def do_algorithm(self, data):
        return sorted(data, reverse=True)

class Context:
    """ Define the interface of interest to clients. """
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy):
        self._strategy = strategy

    def do_some_business_logic(self, data):
        """ Use the Strategy. """
        result = self._strategy.do_algorithm(data)
        print(result)

# Using the Strategy Pattern
data = [23, 5, 89, 7, 34]
context = Context(ConcreteStrategyA())
context.do_some_business_logic(data)  # Output: [5, 7, 23, 34, 89]

context.strategy = ConcreteStrategyB()
context.do_some_business_logic(data)  # Output: [89, 34, 23, 7, 5]
```

### 範例說明

`Context` 可以在不修改自身流程的前提下切換策略。上例中，資料排序可在遞增與遞減演算法之間彈性切換。

## 小結

策略模式可把演算法選擇從主流程中抽離，提升可維護性與擴充性。
