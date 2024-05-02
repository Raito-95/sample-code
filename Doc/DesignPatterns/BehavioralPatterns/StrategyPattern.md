# Strategy Pattern

## Overview

The Strategy Pattern is a behavioral design pattern that enables an algorithm's behavior to be selected at runtime. Rather than implementing a single algorithm directly, code receives run-time instructions as to which in a family of algorithms to use. It is used to define a family of algorithms, encapsulate each one, and make them interchangeable, allowing for the algorithm to vary independently from clients that use it.

## Python Implementation

The Strategy Pattern can be implemented by defining a context class to use different strategies, an interface common to all supported algorithms, and a set of strategies that implement these algorithmic operations.

### Code Example

class Strategy:
    """ Define an interface common to all supported algorithms. """
    def do_algorithm(self, data):
        pass

class ConcreteStrategyA(Strategy):
    """ Implement the algorithm using the Strategy interface. """
    def do_algorithm(self, data):
        return sorted(data)

class ConcreteStrategyB(Strategy):
    """ Implement the algorithm using the Strategy interface. """
    def do_algorithm(self, data):
        return sorted(data, reverse=True)

class Context:
    """ Define the interface of interest to clients. """
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy):
        self._strategy = strategy

    def do_some_business_logic(self, data):
        """ Use the Strategy. """
        result = self._strategy.do_algorithm(data)
        print(result)

# Using the Strategy Pattern
data = [23, 5, 89, 7, 34]
context = Context(ConcreteStrategyA())
context.do_some_business_logic(data)  # Output: [5, 7, 23, 34, 89]

context.strategy = ConcreteStrategyB()
context.do_some_business_logic(data)  # Output: [89, 34, 23, 7, 5]

### Test Results

The example above demonstrates how the Context class uses different strategies to sort a list of integers. ConcreteStrategyA sorts the data in ascending order, while ConcreteStrategyB sorts it in descending order. The Context object changes its behavior according to the strategy it uses, showing flexibility and dynamism in applying different algorithms.

## Conclusion

The Strategy Pattern provides a way to configure a class with one of many behaviors. By defining a series of algorithms and encapsulating each one, switching between different algorithms becomes straightforward. This pattern is particularly useful when you need to dynamically change algorithms used in an application depending on the situation.
