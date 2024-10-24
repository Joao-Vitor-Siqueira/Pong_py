import keyboard
import threading

def get_opposite_key(key):
    if key == 'w':
        return 's'
    elif key == 's':
        return 'w'
    elif key == 'up':
        return 'down'
    else:
        return 'up'

class WindowsListener:
    def __init__(self):
        self.__input_buffer = []
        self.__listener = threading.Thread(target=self.start)
        self.__flag = False

    def listen_key_press(self, key):
        if key.name in ('w', 's', 'up', 'down'):
            if key.name not in self.__input_buffer and get_opposite_key(key.name) not in self.__input_buffer:
                self.__input_buffer.append(key.name)

    def listen_key_release(self, key):
        if key.name in self.__input_buffer:
            self.__input_buffer.remove(key.name)

    def empty(self):
        return len(self.__input_buffer) == 0

    def find(self, val):
        return val in self.__input_buffer

    def listen(self):
        while not self.__flag:
            keyboard.on_press(self.listen_key_press)
            keyboard.on_release(self.listen_key_release)

    def start(self):
        self.__listener.start()

    def join(self):
        self.__flag = True
        self.__listener.join()

    



