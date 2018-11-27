import logging
import os

from .config import config


def set_logger_up():
    """ Sets the logger object up, to log messages to console and to .txt file in logs/ folder.

    :return: the logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    fh_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')

    logs_file = os.path.join(config['PATH']['logs'], "logs.txt")
    fh = logging.FileHandler(logs_file)
    fh.setLevel(logging.WARNING)
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    ch_formatter = logging.Formatter('%(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    logger.info('Initiated logger.')
    return(logger)


def create_new_folder(name, path):
    """
        Creates a new folder if it does not exists yet

    :param name: name of the new folder
    :param path: path of the new folder's parent
    :return: None
    """
    if not os.path.exists(os.path.join(path, name)):
        os.makedirs(os.path.join(path, name))


logger = set_logger_up()
