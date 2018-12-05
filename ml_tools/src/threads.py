from .main import EWHandler

import threading
import logging
logger = logging.getLogger('backend')


class DataProcessThread(threading.Thread):
    """
        This thread processes the Data from track streams set as inputs using ML/DL algorithms
    """

    def __init__(self, debug=False, use_deep=False, mix=False, display_only=True):
        """ Initiates the Thread

        :param debug: (optional) (default False) a kwarg to set the debug mode
        :param use_deep: (optional) (default False) a kwarg to know if simulation should use deep learning
        :param mix: (optional) (default False) a kwarg to know if simulation should mix the use deep learning and db_scan clustering
        """
        self.mix = mix
        self.debug = debug
        self.use_deep = use_deep
        self.display_only = display_only

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
        self.handler.set_sender_function(sender_function)

    def set_deep(self, deep):
        """ Changes the value of the use_deep attribute

        :param deep: A boolean, True if simulation should use deep learning, False if not
        """
        self.use_deep = deep

    def set_mix(self, mix):
        """ Changes the value of the mix attribute

        :param mix: A boolean, True if simulation should mix the use deep learning and db_scan clustering, False if not
        """
        self.mix = mix

    def set_display_only(self, display_only):
        """ Changes the value of the display_only attribute

        :param display_only: A boolean, True if simulation should not do any clustering, False if otherwise
        """
        self.display_only = display_only

    def run(self):
        """ Runs the given thread. 
        """
        self.handler.main(*self.track_streams, debug=self.debug,
                          use_deep=self.use_deep, mix=self.mix, display_only=self.display_only)
        logger.warning('EWHandler Finished !')
        self.handler = EWHandler()

    def stop_thread(self):
        """
        Stops the thread
        """
        try:
            logger.warning("EWHandler got stop order.")
            self.handler.stop()
            logger.warning("EWHandler stopped.")
            return True
        except Exception as err:
            logger.error(err)
            return False

    def pause(self):
        """
        Pauses the thread (goes into a loop, until unpaused)
        """
        try:
            logger.warning("EWHandler got pause order.")
            self.handler.pause()
            logger.warning("EWHandler paused.")
            return True
        except Exception as err:
            logger.error(err)
            return False

    def play(self):
        """
        Unpauses the thread (leaves the loop)
        """
        try:
            logger.warning("EWHandler got play order.")
            self.handler.play()
            logger.warning("EWHandler restarting.")
            return True
        except Exception as err:
            logger.error(err)
            return False
