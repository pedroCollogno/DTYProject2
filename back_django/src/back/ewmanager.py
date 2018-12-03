from ml_tools.threads import DataProcessThread


class EWManager:
    """
    A Manager object, that will store the ongoing Thread and the paths used
    in a run.
    """

    def __init__(self):
        self.paths = []
        self.thread = DataProcessThread(debug=False)
        self.track_streams = []
        self.use_deep = False
        self.mix = False

    def add_path(self, path):
        """ Adds a path to the paths attribute

        :param path: the path to add
        """
        self.paths.append(path)

    def clear_paths(self):
        """ Clears all paths from the paths attribute
        """
        self.paths = []

    def get_paths(self):
        """ Used to get all paths stored by the EWManager object

        :returns: a python list of paths
        """
        return self.paths

    def get_thread(self):
        """ Used to get the thread used here

        :return: a DataProcessThread object
        """
        return self.thread

    def reset_thread(self):
        """ 
        Used to reset the current manager's thread. Called after a simulation is stopped.
        """
        self.thread = DataProcessThread(
            debug=False, use_deep=self.use_deep, mix=self.mix)

    def add_track_stream(self, track_stream):
        """ Adds a track_stream to the track_streams attribute

        :param track_stream: the track_stream to add
        """
        self.track_streams.append(track_stream)

    def clear_track_streams(self):
        """ Clears all track_streams from the track_streams attribute
        """
        self.track_streams = []

    def get_track_streams(self):
        """ Used to get all track_streams stored by the EWManager object

        :returns: a python list of track_streams
        """
        return self.track_streams

    def set_deep(self, deep):
        """ Changes the value of the use_deep attribute

        :param deep: A boolean, True if simulation should use deep learning, False if not
        """
        self.use_deep = deep
        self.thread.set_deep(deep)

    def set_mix(self, mix):
        """ Changes the value of the mix attribute

        :param mix: A boolean, True if simulation should mix the use deep learning and db_scan clustering, False if not
        """
        self.mix = mix
        self.thread.set_mix(mix)
