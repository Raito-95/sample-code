# Factory Method Pattern

## Overview

The Factory Method Pattern is a creational design pattern that provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created. This pattern is particularly useful when there is a need to manage and manipulate collections of objects that are different but at the same time have many common characteristics.

## Python Implementation

The Factory Method Pattern can be implemented by defining an interface or an abstract class with a factory method, which subclasses can then override to produce different types of objects.

### Code Example

```python
class Creator:
    """ Abstract creator class that defines the factory method """
    def factory_method(self):
        raise NotImplementedError("Factory method is not implemented")

    def operation(self):
        """ An operation that calls the factory method to create an object """
        product = self.factory_method()
        result = f"Creator: The same creator's code has just worked with {product.operation()}"
        return result

class ConcreteProductA:
    """ A concrete product class """
    def operation(self):
        return "Result of the ConcreteProductA"

class ConcreteProductB:
    """ Another concrete product class """
    def operation(self):
        return "Result of the ConcreteProductB"

class ConcreteCreatorA(Creator):
    """ Concrete creator that overrides the factory method to create ConcreteProductA """
    def factory_method(self):
        return ConcreteProductA()

class ConcreteCreatorB(Creator):
    """ Concrete creator that overrides the factory method to create ConcreteProductB """
    def factory_method(self):
        return ConcreteProductB()

# Using the Factory Method Pattern
creatorA = ConcreteCreatorA()
print(creatorA.operation())  # Output: Creator: The same creator's code has just worked with Result of the ConcreteProductA

creatorB = ConcreteCreatorB()
print(creatorB.operation())  # Output: Creator: The same creator's code has just worked with Result of the ConcreteProductB
```

### Test Results

The above code demonstrates how the factory method in the Creator abstract class allows for creating objects of ConcreteProductA or ConcreteProductB based on the subclass of Creator used. This pattern enables flexibility and reusability in the creation process.

## Conclusion

The Factory Method Pattern is a robust solution for decoupling the creation of objects from their usage. It allows for specifying what objects to create at runtime and promotes more modular and scalable code. This pattern is especially beneficial when a system needs to introduce new product types without altering existing client code.
