# Decorator Pattern

## Overview

The Decorator Pattern is a structural design pattern that allows behavior to be added to individual objects, either statically or dynamically, without affecting the behavior of other objects from the same class. This pattern is particularly useful for adhering to the Single Responsibility Principle, as it allows functionality to be divided between classes with unique areas of concern.

## Python Implementation

The Decorator Pattern can be implemented by defining a base component interface and then creating several decorator classes that enhance the functionality of objects that implement this interface, without changing the object's core functionality.

### Code Example

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

### Test Results

This example demonstrates how decorators can add new functionalities to objects dynamically while keeping the same interface, showing multiple layers of decorators enhancing the behavior of a simple object.

## Conclusion

The Decorator Pattern is a valuable tool for extending the functionality of objects without the need to modify existing codebase or overload subclassing in systems where new functionalities are frequently required. It provides a flexible alternative to subclassing for extending functionality.
