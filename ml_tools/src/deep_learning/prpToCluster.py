import sys
import os

import tkinter as tk
from tkinter import filedialog

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from ..utils.loading import *
from ..utils.track_utils import *
import processDL as processDL
import model as model
import logging
logger = logging.getLogger('backend')


def main(track_streams, file_name):
    """
    Main function for this script. 
    This is the function mainly used when exporting the deep_learning module.

    :param track_streams: the track_streams from the station to analyse
    :param file_name: the name of the .PRP file, used to name similar files in .PKL format
    :returns: a tuple, containing the labels for clustering the tracks, and the list of the IDS of tracks corresponding to the labels
    """
    processDL.process_data(track_streams, file_name)
    model.test(file_name)
    result = model.train2(file_name)
    return(result)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.update()
    root.destroy()

    file_name = os.path.basename(file_path)

    track_streams = get_track_streams_from_prp(file_path)
    processDL.process_data(track_streams, file_name)
    model.test(file_name)

    logger.info(model.train2(file_name))
