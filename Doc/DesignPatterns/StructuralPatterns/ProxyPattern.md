# Proxy Pattern

## Overview

The Proxy Pattern is a structural design pattern that provides an object representing another object. This surrogate or placeholder object controls access to the original object, allowing it to perform tasks such as lazy initialization, access control, logging, and handling expensive operations. The Proxy Pattern is useful when you want to manage or enhance the interaction between clients and a real object.

## Python Implementation

The Proxy Pattern can be implemented by creating a proxy class that encapsulates the real class, interfacing with it as needed. This can involve forwarding requests to the real object, performing additional operations before or after forwarding, or even deciding not to forward requests based on certain conditions.

### Code Example
```python
class Subject:
    """ Define the common interface for RealSubject and Proxy so that a Proxy can be used anywhere a RealSubject is expected. """
    def request(self):
        pass

class RealSubject(Subject):
    """ Define the real object that the proxy represents. """
    def request(self):
        return "RealSubject: Handling request."

class Proxy(Subject):
    """ The Proxy maintains a reference to an object of the RealSubject class and controls access to it. """
    def __init__(self, real_subject):
        self._real_subject = real_subject

    def request(self):
        if self.check_access():
            response = self._real_subject.request()
            self.log_access()
            return f"Proxy: Log start -> {response} -> Log end"
        else:
            return "Proxy: Access denied."

    def check_access(self):
        """ Simulate the access control. """
        # Implement the condition checks for accessing the real subject.
        return True  # Access is granted

    def log_access(self):
        """ Log the access details. """
        print("Proxy: Logging access to the real subject.")

# Using the Proxy Pattern
real_subject = RealSubject()
proxy = Proxy(real_subject)
print(proxy.request())  # Output: Proxy: Log start -> RealSubject: Handling request. -> Log end
```

### Test Results

The example above shows how the Proxy class can control access to the RealSubject class. It can perform actions before and after forwarding the request to the real subject, such as checking permissions and logging.

## Conclusion

The Proxy Pattern is useful for managing the access and functionality of an object without altering its code. It is particularly valuable in scenarios where you want to add or enhance the behavior of objects dynamically, or when direct access to the object is not desired or possible due to resource constraints or security considerations.
