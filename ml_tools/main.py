import matplotlib
matplotlib.use("TkAgg")
from tkinter import filedialog
import tkinter as tk
import sys
import os

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.join(file_dir, 'src'))

from src import main, threads
from utils import station_utils
from utils import loading as load
from utils.log import logger
from utils.plotting import display_alternates


def mock_sender_function(json_obj):
    """
    A mock sender_function, to be able to test the ML algorithms without running the backend.
    """
    logger.debug(json_obj)


"""This part runs if you run 'python main.py' in the console"""
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames()
    root.update()

    display_alternates(*file_paths)