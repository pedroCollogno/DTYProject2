import logging
import os

from .config import config


def set_logger_up():
    """ Sets the logger object up, to log messages to console and to .txt file in logs/ folder.

    :return: the logger
    """
    logger = logging.getLogger('backend')
    logger.setLevel(logging.DEBUG)

    fh_formatter = logging.Formatter(
        '%(asctime)s - %(name)% - %(levelname)s - %(message)s')

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

    # Adding filehandler to server and worker loggers.
    # These are loggers created by the project's Django backend
    server_logger = logging.getLogger('server')
    server_logger.addHandler(fh)

    worker_logger = logging.getLogger('worker')
    worker_logger.addHandler(fh)


def create_new_folder(name, path):
    """
        Creates a new folder if it does not exists yet

    :param name: name of the new folder
    :param path: path of the new folder's parent
    :return: None
    """
    if not os.path.exists(os.path.join(path, name)):
        os.makedirs(os.path.join(path, name))


set_logger_up()
