# Adapter Pattern

## Overview

The Adapter Pattern is a structural design pattern that allows objects with incompatible interfaces to collaborate. It works by creating a middle-layer that translates, or "adapts," the interface of one class to be used as another interface. This pattern is particularly useful when wanting to use existing classes without modifying their source code.

## Python Implementation

The Adapter Pattern can be implemented by defining an adapter class that wraps the existing class and provides the expected interface through delegation.

### Code Example
```python
class Target:
    """ The Target defines the domain-specific interface used by the client code. """
    def request(self):
        return "Target: The default target's behavior."

class Adaptee:
    """ The Adaptee contains some useful behavior, but its interface is incompatible
    with the existing client code. The Adaptee needs some adaptation before the client code can use it. """
    def specific_request(self):
        return ".eetpadA eht fo roivaheb laicepS"

class Adapter(Target):
    """ The Adapter makes the Adaptee's interface compatible with the Target's interface via inheritance. """
    def __init__(self, adaptee):
        self._adaptee = adaptee

    def request(self):
        return f"Adapter: (TRANSLATED) {self._adaptee.specific_request()[::-1]}"

# Using the Adapter Pattern
adaptee = Adaptee()
print(f"Adaptee: {adaptee.specific_request()}")  # Adaptee's existing behavior doesn't match the client's expectations.

adapter = Adapter(adaptee)
print(adapter.request())  # Output: Adapter: (TRANSLATED) Special behavior of the Adaptee.
```

### Test Results

This example illustrates how the Adapter pattern allows the client to use the Adaptee's special behavior through the Target interface by reversing the string returned by the Adaptee's specific request method. This adaptation lets the client interact with the Adaptee without any direct modifications to its source code.

## Conclusion

The Adapter Pattern provides a flexible solution to interface incompatibility issues between classes. It enables objects to work together that couldn't otherwise because of mismatched interfaces. The use of this pattern makes it easier to introduce new class adapters without changing the client code.
