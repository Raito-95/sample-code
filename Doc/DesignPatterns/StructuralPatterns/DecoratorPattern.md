# 裝飾者模式（Decorator Pattern）

## 概觀

裝飾者模式是一種結構型設計模式，可在不修改原始類別的情況下，動態為物件加上額外行為。

## Python 實作

可先定義共同元件介面，再建立多個裝飾者包裹元件，逐層擴充功能。

### 程式範例
```python
class Component:
    """ Defines the interface for objects that can have responsibilities added to them dynamically. """
    def operation(self):
        pass

class ConcreteComponent(Component):
    """ Defines an object to which additional responsibilities can be attached. """
    def operation(self):
        return "ConcreteComponent: Base Operation"

class Decorator(Component):
    """ Maintains a reference to a Component object and defines an interface that conforms to Component's interface. """
    def __init__(self, component):
        self._component = component

    def operation(self):
        return self._component.operation()

class ConcreteDecoratorA(Decorator):
    """ Adds responsibilities to the component. """
    def operation(self):
        return f"ConcreteDecoratorA: Enhanced Operation ({self._component.operation()})"

class ConcreteDecoratorB(Decorator):
    """ Adds responsibilities to the component. """
    def operation(self):
        return f"ConcreteDecoratorB: Enhanced Operation ({self._component.operation()})"

# Using the Decorator Pattern
simple = ConcreteComponent()
print(simple.operation())  # Output: ConcreteComponent: Base Operation

decorated = ConcreteDecoratorA(simple)
print(decorated.operation())  # Output: ConcreteDecoratorA: Enhanced Operation (ConcreteComponent: Base Operation)

more_decorated = ConcreteDecoratorB(decorated)
print(more_decorated.operation())  # Output: ConcreteDecoratorB: Enhanced Operation (ConcreteDecoratorA: Enhanced Operation (ConcreteComponent: Base Operation))
```

### 範例說明

範例展示如何透過多層裝飾者在同一介面下逐步擴充功能，而不影響原始元件。

## 小結

裝飾者模式提供比繼承更彈性的擴充方式，適合功能組合頻繁變動的系統。
