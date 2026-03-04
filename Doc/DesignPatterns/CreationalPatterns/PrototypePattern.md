# 原型模式（Prototype Pattern）

## 概觀

原型模式是一種建立型設計模式，透過複製既有物件（Clone）來產生新物件。當物件建立成本高或初始化流程複雜時特別實用。

## Python 實作

Python 可搭配 `copy` 模組進行淺拷貝或深拷貝。以下示範以深拷貝方式建立新實例。

### 程式範例

```python
import copy

class Prototype:
    def __init__(self):
        self._objects = {}

    def register_object(self, name, obj):
        """ Register an object with a specific name """
        self._objects[name] = obj

    def unregister_object(self, name):
        """ Remove an object from the registry """
        del self._objects[name]

    def clone(self, name, **attrs):
        """ Clone a registered object and update its attributes """
        obj = copy.deepcopy(self._objects[name])
        obj.__dict__.update(attrs)
        return obj

class Car:
    def __init__(self, model, engine):
        self.model = model
        self.engine = engine

    def __str__(self):
        return f'Model: {self.model}, Engine: {self.engine}'

# Using the Prototype Pattern
prototype = Prototype()
prototype.register_object('skoda', Car('Skoda Octavia', '1.4 TSI'))

car1 = prototype.clone('skoda')
car2 = prototype.clone('skoda', engine='2.0 TSI')

print(car1)  # Output: Model: Skoda Octavia, Engine: 1.4 TSI
print(car2)  # Output: Model: Skoda Octavia, Engine: 2.0 TSI
```

### 範例說明

`Prototype` 管理已註冊的原型物件，`clone` 可快速產生副本並覆寫部分屬性。

## 小結

原型模式可減少重複建構成本，適合需要大量相似物件、但只在少數欄位不同的情境。
