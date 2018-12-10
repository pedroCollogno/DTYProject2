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
        self.paused = False
        self.processes = self.get_python_processes()

        self.process_profiler = process_profiler
        threading.Thread.__init__(self)

    def get_python_processes(self):
        """ Used to know about all processes that are running with Python

        :return: A list, containing all Python processes running on this machine
        """
        processes = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(
                    attrs=['pid', 'name', 'username'])
                if pinfo['name'] is not None:
                    if 'Python' in pinfo['name'] or 'python' in pinfo['name'] : # Monitor all Python processes
                        processes.append(proc)
            except psutil.NoSuchProcess as err:
                logger.error(err)
        return processes

    def measure(self):
        """
        Make a measurement for the process, and send the results to the ProcessProfiler
        """
        total_mem_info = 0
        total_mem_percent = 0
        total_cpu_percent = 0
        for process in self.processes:
            total_mem_info += process.memory_info().rss
            total_mem_percent += process.memory_percent()
            total_cpu_percent += process.cpu_percent()

        self.process_profiler.add_memory_info(total_mem_info / 1e6)  # Memory usage in MegaBytes
        self.process_profiler.add_memory_percent(total_mem_percent)
        self.process_profiler.add_cpu_percent(total_cpu_percent)

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
