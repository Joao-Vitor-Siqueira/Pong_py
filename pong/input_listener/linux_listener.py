from pynput.keyboard import Listener


def get_opposite_key(key):
    if key == "'W'":
        return "'S'"
    elif key == "'S'":
        return "'W'"
    elif key == 'KEY.UP':
        return 'KEY.DOWN'
    else:
        return 'KEY.UP'


class LinuxListener:
    def __init__(self):
        self.__input_buffer = set()  # Changed to a set
        self.__listener = Listener(on_press=self.listen_key_press, on_release=self.listen_key_release)

    def listen_key_press(self, key):
        if not isinstance(key, str):
            key = str(key).upper()

        # Use the set to manage keys
        if (key in ("'W'", "'S'", 'KEY.UP', 'KEY.DOWN') and
                key not in self.__input_buffer and
                get_opposite_key(key) not in self.__input_buffer):
            self.__input_buffer.add(key)

    def listen_key_release(self, key):
        if not isinstance(key, str):
            key = str(key).upper()

        self.__input_buffer.discard(key)

    def empty(self):
        return len(self.__input_buffer) == 0

    def find(self, val):
        return val in self.__input_buffer

    def start(self):
        self.__listener.start()

    def join(self):
        self.__listener.join(timeout=0.15)
