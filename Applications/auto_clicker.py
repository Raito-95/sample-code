import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Listener, Key

class AutoClicker:
    def __init__(self, test_mode=False):
        """
        Initialize the auto clicker.
        
        :param test_mode: If True, run in test mode that does not perform actual clicks.
        """
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.clicking = False
        self.test_mode = test_mode
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def ctrl_click(self):
        """
        Perform a control click, or simulate a click in test mode.
        """
        if self.test_mode:
            print("Test click at {}".format(time.ctime()))
        else:
            if not self.clicking:
                self.keyboard.press(Key.ctrl)
                print("Ctrl key pressed")
            self.mouse.press(Button.left)
            time.sleep(0.1)
            self.mouse.release(Button.left)
            time.sleep(0.1)

    def on_press(self, key):
        """
        Handle the press event of keys.
        
        :param key: The key that was pressed.
        """
        try:
            if key.char == 'z':
                self.clicking = True
                print("Start auto clicking")
        except AttributeError:
            pass

    def on_release(self, key):
        """
        Handle the release event of keys.
        
        :param key: The key that was released.
        """
        try:
            if key.char == 'x' and self.clicking:
                if not self.test_mode:
                    self.keyboard.release(Key.ctrl)
                    print("Ctrl key released")
                self.clicking = False
                print("Stop auto clicking")
        except AttributeError:
            pass

    def run(self):
        """
        Run the main loop.
        """
        while True:
            if self.clicking:
                self.ctrl_click()
            time.sleep(0.1)

if __name__ == "__main__":
    # Set test_mode to True to start in test mode
    clicker = AutoClicker(test_mode=False)
    clicker.run()
