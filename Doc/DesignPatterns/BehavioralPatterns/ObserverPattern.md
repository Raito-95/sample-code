# Observer Pattern

## Overview

The Observer Pattern is a behavioral design pattern in which an object, known as the subject, maintains a list of its dependents, called observers, and notifies them automatically of any state changes, usually by calling one of their methods. It is used primarily to implement distributed event-handling systems, where the subject needs to notify an open-ended number of "observers" about the occurrence of some event.

## Python Implementation

The Observer Pattern can be implemented in Python by creating a subject class that keeps track of observers and notifies them of changes, and observer classes that define the updating interface.

### Code Example

class Subject:
    """ Represents what is being 'observed' """
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        """ Attach an observer to the subject. """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """ Detach an observer from the subject. """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self):
        """ Notify all observers about an event. """
        for observer in self._observers:
            observer.update(self)

class ConcreteSubject(Subject):
    """ The 'Subject' that is being observed """
    def __init__(self):
        super().__init__()
        self._subject_state = None

    @property
    def subject_state(self):
        return self._subject_state

    @subject_state.setter
    def subject_state(self, arg):
        self._subject_state = arg
        self.notify()

class Observer:
    """ Abstract observer """
    def update(self, subject):
        pass

class ConcreteObserverA(Observer):
    """ Concrete observer """
    def update(self, subject):
        print("ConcreteObserverA: Reacted to the event")

class ConcreteObserverB(Observer):
    """ Concrete observer """
    def update(self, subject):
        print("ConcreteObserverB: Reacted to the event")

# Using the Observer Pattern
subject = ConcreteSubject()
observer_a = ConcreteObserverA()
observer_b = ConcreteObserverB()

subject.attach(observer_a)
subject.attach(observer_b)

subject.subject_state = "state changed"
# Output: ConcreteObserverA: Reacted to the event
#         ConcreteObserverB: Reacted to the event

### Test Results

The example above shows how ConcreteObserverA and ConcreteObserverB are notified of changes in ConcreteSubject. When the `subject_state` is set, both attached observers are updated via their `update` method.

## Conclusion

The Observer Pattern is useful for scenarios where a change to one object requires changing others, and particularly when the number of objects that need to be changed is unknown or changes dynamically. It provides an excellent way to create a loosely coupled system where the subject and observers can interact without being tightly bound.
