# 進階 Python 物件導向

本篇延伸基礎 OOP，說明四個常見進階主題：封裝、繼承、多型、魔術方法。

## 1. 封裝（Encapsulation）

封裝的目標是保護內部狀態，透過方法控制讀寫，避免資料被任意破壞。

```python
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.__odometer_reading = 0

    def get_odometer(self):
        return self.__odometer_reading

    def set_odometer(self, mileage):
        if mileage >= self.__odometer_reading:
            self.__odometer_reading = mileage

    def increment_odometer(self, miles):
        if miles >= 0:
            self.__odometer_reading += miles
```

## 2. 繼承（Inheritance）

子類別可重用父類別行為，並擴充新能力。

```python
class ElectricCar(Car):
    def __init__(self, make, model, year, battery_size=75):
        super().__init__(make, model, year)
        self.battery_size = battery_size

    def describe_battery(self):
        return f"This car has a {self.battery_size}-kWh battery."
```

## 3. 多型（Polymorphism）

不同物件可回應同一介面，呼叫端不需知道具體類型。

```python
class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

def make_animal_speak(animal):
    print(animal.speak())
```

## 4. 魔術方法（Magic Methods）

魔術方法讓自訂類別與 Python 內建語法整合，例如 `str()`、`len()`。

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __str__(self):
        return f"'{self.title}' by {self.author}"

    def __len__(self):
        return len(self.title)
```

## 小結

- 封裝提升資料安全性
- 繼承提升重用性
- 多型降低耦合
- 魔術方法提升可讀性與 API 一致性
