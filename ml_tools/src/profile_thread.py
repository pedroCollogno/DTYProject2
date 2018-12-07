
import threading
import psutil
import time

import logging
logger = logging.getLogger('backend')


class ProfilerThread(threading.Thread):
    """
    Profiler Thread, used to make performance measurements.
    """

    def __init__(self, process_profiler):
        """ Initiate the ProfilerThread object

        :param pid: the ID of the process to profile
        :param process_profiler: the parent process_profiler, that created the Thread
        """
        self.running = True
        self.process = psutil.Process()

        self.process_profiler = process_profiler
        threading.Thread.__init__(self)

    def measure(self):
        """
        Make a measurement for the process
        """
        self.process_profiler.add_memory_info(self.process.memory_info().rss /  # Replace by "Add To Manager" functions
                                              1e6)  # Memory usage in MegaBytes
        self.process_profiler.add_memory_percent(self.process.memory_percent())
        self.process_profiler.add_cpu_percent(self.process.cpu_percent())
        self.process_profiler.add_cpu_times(self.process.cpu_times().user)

    def run(self):
        """
        Makes measurements regularly on the targetted process
        """
        while(self.running):
            if not self.paused:
                self.measure()
            time.sleep(0.5)
        self.measure()

    def stop(self):
        """
        Stops the instance of ProfilerThread
        """
        self.running = False

    def play(self):
        """
        Unpauses the thread (leaves the loop)
        """
        self.paused = False

    def pause(self):
        """
        Pauses the thread (goes into a loop, until unpaused)
        """
        self.paused = True
