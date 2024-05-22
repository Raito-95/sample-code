# Python物件導向基礎

學習Python物件導向的基礎，可以從了解以下幾個關鍵概念開始：類別（Class）、物件（Object）、屬性（Attribute）和方法（Method）。

## 1. 類別（Class）

類別是物件的藍圖或模板。它定義了物件的屬性和方法。
```python
class Dog:
    # 類別屬性
    species = 'Canis familiaris'

    # 初始化方法
    def __init__(self, name, age):
        self.name = name    # 實例屬性
        self.age = age      # 實例屬性

    # 實例方法
    def description(self):
        return f"{self.name} is {self.age} years old"

    # 實例方法
    def speak(self, sound):
        return f"{self.name} says {sound}"
```
## 2. 物件（Object）

物件是類別的實例。有了類別之後，可以創建多個物件，每個物件都有自己的屬性值。
```python
# 創建物件
dog1 = Dog("Buddy", 2)
dog2 = Dog("Molly", 5)

# 訪問物件屬性和方法
print(dog1.description())  # Buddy is 2 years old
print(dog2.speak("Woof"))  # Molly says Woof
```

## 3. 屬性（Attribute）

屬性是類別中變量。它們可以是類別屬性（所有實例共享）或實例屬性（每個實例獨有）。
```python
print(dog1.species)  # Canis familiaris
print(dog2.species)  # Canis familiaris
print(dog1.name)     # Buddy
print(dog2.name)     # Molly
```

## 4. 方法（Method）

方法是類別中定義的函數，用於操作物件的屬性或執行操作。
```python
print(dog1.description())  # Buddy is 2 years old
print(dog2.description())  # Molly is 5 years old
```

## 5. 繼承（Inheritance）

繼承允許我們定義一個類別，該類別可以繼承另一個類別的屬性和方法。
```python
class Puppy(Dog):
    def __init__(self, name, age, training_level):
        super().__init__(name, age)  # 繼承父類的屬性
        self.training_level = training_level  # 新屬性

    def description(self):
        return f"{self.name} is {self.age} years old and is at training level {self.training_level}"

# 創建子類物件
puppy1 = Puppy("Max", 1, "beginner")

print(puppy1.description())  # Max is 1 years old and is at training level beginner
print(puppy1.speak("Yip"))  # Max says Yip
```
