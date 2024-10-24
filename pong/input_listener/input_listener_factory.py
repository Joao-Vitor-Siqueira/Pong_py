import platform
from pong.input_listener.linux_listener import LinuxListener
from pong.input_listener.windows_listener import WindowsListener

class InputListenerFactory:
    def __init__(self):
        self.os = platform.system()
        self.listener = None

    def get_listener(self):
        if not self.listener:
            if self.os == 'Windows':
                return WindowsListener()
            else:
                return LinuxListener()


