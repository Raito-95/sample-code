# 進階Python物件導向

在學習了基本概念後，可以進一步了解一些進階的Python物件導向特性，如封裝（Encapsulation）、繼承（Inheritance）、多型（Polymorphism）和魔術方法（Magic Methods）。

## 1. 封裝（Encapsulation）

封裝是將物件的狀態（屬性）和行為（方法）捆綁在一起，並對其進行訪問控制。這可以通過定義私有屬性和方法來實現。
```python
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.__odometer_reading = 0  # 私有屬性

    def get_odometer(self):
        return self.__odometer_reading

    def set_odometer(self, mileage):
        if mileage >= self.__odometer_reading:
            self.__odometer_reading = mileage
        else:
            print("You can't roll back an odometer!")

    def increment_odometer(self, miles):
        if miles >= 0:
            self.__odometer_reading += miles
        else:
            print("You can't roll back an odometer!")

car = Car('Toyota', 'Camry', 2020)
print(car.get_odometer())  # 0
car.set_odometer(15000)
print(car.get_odometer())  # 15000
```

## 2. 繼承（Inheritance）

繼承允許我們創建一個新類別，該類別基於一個已經存在的類別。這樣可以重用父類的屬性和方法。
```python
class ElectricCar(Car):
    def __init__(self, make, model, year, battery_size=75):
        super().__init__(make, model, year)
        self.battery_size = battery_size  # 新屬性

    def describe_battery(self):
        return f"This car has a {self.battery_size}-kWh battery."

# 創建子類物件
my_tesla = ElectricCar('Tesla', 'Model S', 2020)

print(my_tesla.describe_battery())  # This car has a 75-kWh battery.
print(my_tesla.get_odometer())  # 0
my_tesla.set_odometer(5000)
print(my_tesla.get_odometer())  # 5000
```

## 3. 多型（Polymorphism）

多型允許我們使用統一的接口來調用不同類別中的方法。這使得程式設計更加靈活和可擴展。
```python
class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

def make_animal_speak(animal):
    print(animal.speak())

dog = Dog()
cat = Cat()

make_animal_speak(dog)  # Woof!
make_animal_speak(cat)  # Meow!
```

## 4. 魔術方法（Magic Methods）

魔術方法是一種特殊的方法，它們是由雙下劃線包圍的，並且具有特定的名稱和行為。最常見的魔術方法是初始化方法 __init__，還有很多其他有用的魔術方法。
```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __str__(self):
        return f"'{self.title}' by {self.author}"

    def __len__(self):
        return len(self.title)

book = Book('1984', 'George Orwell')
print(book)  # '1984' by George Orwell
print(len(book))  # 4
```
