import keyboard

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
        self.__input_buffer = set()

    def listen_key_event(self, event):
        key = event.name
        if event.event_type == 'down':

            if key in ('w', 's', 'up', 'down'):
                if key not in self.__input_buffer and get_opposite_key(key) not in self.__input_buffer:
                    self.__input_buffer.add(key)

        elif event.event_type == 'up':
            self.__input_buffer.discard(key)

    def empty(self):
        return len(self.__input_buffer) == 0

    def find(self, key):
        return key in self.__input_buffer

    def start(self):
        keyboard.hook(self.listen_key_event)

    def join(self):
        keyboard.unhook(self.listen_key_event)





