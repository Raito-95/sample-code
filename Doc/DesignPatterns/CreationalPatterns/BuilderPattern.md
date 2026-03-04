# 建造者模式（Builder Pattern）

## 概觀

建造者模式是一種建立型設計模式，用來分離「複雜物件的建構流程」與「最終表示」。呼叫端只需指定要建什麼，不必關注每個零件如何組裝。

## Python 實作

常見結構包含 `Director`（控制建構順序）與 `Builder`（負責具體零件建造）。

### 程式範例

```python
# Builder Pattern
class Director:
    def __init__(self, builder):
        self._builder = builder

    def construct_car(self):
        self._builder.create_new_car()
        self._builder.add_model()
        self._builder.add_tires()
        self._builder.add_engine()

class Builder:
    def __init__(self):
        self.car = None

    def create_new_car(self):
        self.car = Car()

class CarBuilder(Builder):
    def add_model(self):
        self.car.model = 'SUV'

    def add_tires(self):
        self.car.tires = 'Off-road tires'

    def add_engine(self):
        self.car.engine = 'Turbo engine'

class Car:
    def __init__(self):
        self.model = None
        self.tires = None
        self.engine = None

    def __str__(self):
        return '{} | {} | {}'.format(self.model, self.tires, self.engine)

# Using the Builder Pattern
builder = CarBuilder()
director = Director(builder)
director.construct_car()
car = builder.car
print(car)  # Output: SUV | Off-road tires | Turbo engine
```

### 範例說明

上例由 `Director` 控制建造步驟，`CarBuilder` 負責填入車型、輪胎與引擎設定。

## 小結

建造者模式適合建構步驟多、組合複雜的物件，可讓流程更模組化，也便於替換不同建造策略。
