import sys
import os

import tkinter as tk
from tkinter import filedialog

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from utils.loading import *
from utils.track_utils import *
from utils.log import logger
import processDL as processDL
import model as model


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    file_name = os.path.basename(file_path)

    track_streams = get_track_streams_from_prp(file_path)
    processDL.process_data(track_streams, file_name)
    model.test(file_name)

    logger.info(model.train2(file_name))
