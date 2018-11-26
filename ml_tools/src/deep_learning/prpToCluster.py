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
import processDL as processDL
import model as model


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    file_name = os.path.basename(file_path)

    tsexs = get_track_stream_exs_from_prp(file_path)
    processDL.process_data(tsexs, file_name)
    model.test(file_name)
    print(model.train2(file_name))
