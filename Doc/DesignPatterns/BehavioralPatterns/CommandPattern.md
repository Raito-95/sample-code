# Command Pattern

## Overview

The Command Pattern is a behavioral design pattern that turns a request into a stand-alone object that contains all information about the request. This transformation allows you to parameterize methods with different requests, delay or queue a request's execution, and support undoable operations. It is particularly useful for implementing things like transactional behavior and managing operations on data.

## Python Implementation

The Command Pattern can be implemented by defining a command interface with an execute method, and concrete command classes that encapsulate a request by binding together all of the information needed to perform the action.

### Code Example
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

### Test Results

The example above demonstrates how the Invoker issues commands to start and finish its operations, with commands encapsulating all the necessary details. `SimpleCommand` handles simple printing, while `ComplexCommand` involves more complex interaction with the `Receiver`.

## Conclusion

The Command Pattern is invaluable for designing flexible and extensible systems, as it decouples the sender of a request from its receivers, allowing a variety of operations to be performed. It supports undo operations, logging, and transactional behaviors.
