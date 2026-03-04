# Python 物件導向基礎

這份教材介紹 Python OOP 的四個核心：`class`、`object`、`attribute`、`method`。

## 1. 類別（Class）

類別是建立物件的藍圖，用來定義共同的資料與行為。

```python
class Dog:
    species = "Canis familiaris"  # 類別屬性：所有 Dog 物件共用

    def __init__(self, name, age):
        self.name = name  # 實例屬性
        self.age = age    # 實例屬性

    def description(self):
        return f"{self.name} is {self.age} years old"

    def speak(self, sound):
        return f"{self.name} says {sound}"
```

## 2. 物件（Object）

物件是由類別建立出來的實體，每個物件可以有自己的狀態。

```python
dog1 = Dog("Buddy", 2)
dog2 = Dog("Molly", 5)

print(dog1.description())  # Buddy is 2 years old
print(dog2.speak("Woof"))  # Molly says Woof
```

## 3. 屬性（Attribute）

屬性是物件儲存資料的欄位，可分為類別屬性與實例屬性。

```python
print(dog1.species)  # Canis familiaris (類別屬性)
print(dog2.species)  # Canis familiaris
print(dog1.name)     # Buddy (實例屬性)
print(dog2.name)     # Molly
```

## 4. 方法（Method）

方法是定義在類別中的函式，描述物件可以執行的行為。

```python
print(dog1.description())  # Buddy is 2 years old
print(dog2.description())  # Molly is 5 years old
```

## 小結

- 用 `class` 定義資料與行為
- 由類別建立 `object` 作為具體實例
- 透過 `attribute` 儲存狀態
- 透過 `method` 操作資料與行為
