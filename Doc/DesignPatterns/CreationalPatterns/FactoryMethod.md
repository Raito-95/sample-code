# 工廠方法模式（Factory Method Pattern）

## 概觀

工廠方法模式是一種建立型設計模式。它在父類別中定義建立物件的介面，並讓子類別決定實際要建立哪種產品。

## Python 實作

通常會有一個創建者（Creator）定義 `factory_method`，各具體創建者覆寫此方法來回傳不同產品。

### 程式範例

```python
class Creator:
    """ Abstract creator class that defines the factory method """
    def factory_method(self):
        raise NotImplementedError("Factory method is not implemented")

    def operation(self):
        """ An operation that calls the factory method to create an object """
        product = self.factory_method()
        result = f"Creator: The same creator's code has just worked with {product.operation()}"
        return result

class ConcreteProductA:
    """ A concrete product class """
    def operation(self):
        return "Result of the ConcreteProductA"

class ConcreteProductB:
    """ Another concrete product class """
    def operation(self):
        return "Result of the ConcreteProductB"

class ConcreteCreatorA(Creator):
    """ Concrete creator that overrides the factory method to create ConcreteProductA """
    def factory_method(self):
        return ConcreteProductA()

class ConcreteCreatorB(Creator):
    """ Concrete creator that overrides the factory method to create ConcreteProductB """
    def factory_method(self):
        return ConcreteProductB()

# Using the Factory Method Pattern
creatorA = ConcreteCreatorA()
print(creatorA.operation())  # Output: Creator: The same creator's code has just worked with Result of the ConcreteProductA

creatorB = ConcreteCreatorB()
print(creatorB.operation())  # Output: Creator: The same creator's code has just worked with Result of the ConcreteProductB
```

### 範例說明

呼叫端面對的是 `Creator` 介面，不需要知道實際產品類別，能降低建立流程與使用流程的耦合。

## 小結

工廠方法模式能提升彈性，讓系統在不修改既有客戶端程式碼下擴充新產品型別。
