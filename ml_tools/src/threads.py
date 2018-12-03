from .main import EWHandler

import threading
import logging
logger = logging.getLogger('backend')


class DataProcessThread(threading.Thread):
    """
        This thread processes the Data from track streams set as inputs using ML/DL algorithms
    """

    def __init__(self, debug=False):
        """ Initiates the Thread

        :param debug: (optional) a kwarg to set the debug mode
        """
        self.debug = debug
        self.handler = EWHandler()
        threading.Thread.__init__(self)

    def set_track_streams(self, *args):
        """
        :param *args: an unpacked list of all TrackStream objects to analyse
        """
        self.track_streams = args

    def set_sender_function(self, sender_function):
        """ Sets the function used by the backend to send data to the frontend

        :param sender_function: the function used by the backend to send data
        """
        self.sender_function = sender_function

    def run(self):
        """ Runs the given thread. 
        """
        self.handler.main(*self.track_streams, debug=self.debug,
                          sender_function=self.sender_function)
        logger.warning('EWHandler Finished !')
        self.__dict__.clear()

    def stop_thread(self):
        logger.warning("EWHandler got stop order.")
        self.handler.stop()
        logger.warning("EWHandler stopped.")
        return True
