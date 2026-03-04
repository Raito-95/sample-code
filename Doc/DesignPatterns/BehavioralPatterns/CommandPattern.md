# 命令模式（Command Pattern）

## 概觀

命令模式是一種行為型設計模式，將「請求」封裝成獨立物件，讓你可以用一致方式處理不同操作。透過這種封裝，你可以延遲執行、排隊執行，甚至支援撤銷（Undo）等能力。

## Python 實作

命令模式通常包含一個命令介面（例如 `execute` 方法），再由具體命令類別封裝實際操作；呼叫端只需觸發命令，不需知道細節。

### 程式範例
```python
class Command:
    """ The Command interface declares a method for executing a command. """
    def execute(self):
        pass

class SimpleCommand(Command):
    """ Concrete Commands implement various kinds of requests. """
    def __init__(self, payload):
        self._payload = payload

    def execute(self):
        print(f"SimpleCommand: See, I can do simple things like printing ({self._payload})")

class ComplexCommand(Command):
    """ Some commands can delegate more complex operations to other objects, called 'receivers'. """
    def __init__(self, receiver, a, b):
        self._receiver = receiver
        self._a = a
        self._b = b

    def execute(self):
        print("ComplexCommand: Complex stuff should be done by a receiver object.")
        self._receiver.do_something(self._a)
        self._receiver.do_something_else(self._b)

class Receiver:
    """ The Receiver classes contain some important business logic. """
    def do_something(self, a):
        print(f"\tReceiver: Working on ({a})")

    def do_something_else(self, b):
        print(f"\tReceiver: Also working on ({b})")

class Invoker:
    """ The Invoker is associated with one or several commands. It sends a request to the command. """
    def __init__(self):
        self._on_start = None
        self._on_finish = None

    @property
    def on_start(self):
        return self._on_start

    @on_start.setter
    def on_start(self, command: Command):
        self._on_start = command

    @property
    def on_finish(self):
        return self._on_finish

    @on_finish.setter
    def on_finish(self, command: Command):
        self._on_finish = command

    def do_something_important(self):
        print("Invoker: Does anybody want something done before I begin?")
        if self._on_start:
            self._on_start.execute()

        print("Invoker: ...doing something really important...")

        print("Invoker: Does anybody want something done after I finish?")
        if self._on_finish:
            self._on_finish.execute()

# Using the Command Pattern
invoker = Invoker()
invoker.on_start = SimpleCommand("Say Hi!")
receiver = Receiver()
invoker.on_finish = ComplexCommand(receiver, "Send email", "Save report")

invoker.do_something_important()
```

### 範例說明

上例展示 `Invoker` 在流程前後觸發不同命令，`SimpleCommand` 處理簡單動作，`ComplexCommand` 則委派給 `Receiver` 處理實際商業邏輯。

## 小結

命令模式可降低呼叫端與執行端的耦合，提升系統擴充性，也常用於撤銷、操作記錄與工作佇列等場景。
