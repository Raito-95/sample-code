# 觀察者模式（Observer Pattern）

## 概觀

觀察者模式是一種行為型設計模式。主題物件（Subject）維護一組觀察者（Observer），當主題狀態改變時，會主動通知所有觀察者更新。

## Python 實作

可建立一個主題類別管理訂閱/取消訂閱，並在狀態改變時呼叫所有觀察者的更新方法。

### 程式範例
```python
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
```

### 範例說明

當 `ConcreteSubject` 的 `subject_state` 被設定時，所有已訂閱的觀察者都會透過 `update` 方法收到通知。

## 小結

觀察者模式適合事件通知、多方同步更新等情境，可在不緊耦合的前提下讓主題與觀察者協作。
