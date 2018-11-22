
import matplotlib
matplotlib.use("TkAgg")
from tkinter import filedialog
import tkinter as tk

from src import main, threads
from src.utils import station_utils
from src.utils import loading as load
from src.utils.log import logger


def mock_sender_function(json_obj):
    logger.debug(json_obj)


"""This part runs if you run 'python main.py' in the console"""
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames()

    track_streams = []
    for path in file_paths:
        if path is not None:
            track_stream = load.get_track_streams_from_prp(path)
            track_streams.append(track_stream)
