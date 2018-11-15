import threading

from .main import main


class DataProcessThread(threading.Thread):
    def __init__(self, *args, debug=False):
        self.track_stream_ex_s = args
        self.debug = debug
        threading.Thread.__init__(self)

    def set_sender_function(self, sender_function):
        self.sender_function = sender_function

    def run(self):
        main(*self.track_stream_ex_s, debug=self.debug,
             sender_function=self.sender_function)
        self.__dict__.clear()
        print('Finished !')

    def join(self):
        threading.Thread.join(self)
