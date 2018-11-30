import threading

from .main import main, stop


class DataProcessThread(threading.Thread):
    """
        This thread processes the Data from track streams set as inputs using ML/DL algorithms
    """

    def __init__(self, *args, debug=False):
        """ Initiates the Thread

        :param *args: an unpacked list of all TrackStream objects to analyse
        :param debug: (optional) a kwarg to set the debug mode
        """
        self.track_streams = args
        self.debug = debug
        threading.Thread.__init__(self)

    def set_sender_function(self, sender_function):
        """ Sets the function used by the backend to send data to the frontend

        :param sender_function: the function used by the backend to send data
        """
        self.sender_function = sender_function

    def run(self):
        """ Runs the given thread. 
        """
        main(*self.track_streams, debug=self.debug,
             sender_function=self.sender_function)
        self.__dict__.clear()
        print('Finished !')

    def stop_thread(self):
        print("Stop")
        stop()
        print("Stopped")
        self.join()
