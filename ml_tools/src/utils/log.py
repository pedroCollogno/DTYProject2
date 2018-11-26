import logging
import os
import json

with open('config.json', 'r') as f:
    config = json.load(f)


def set_logger_up():
    """ Sets the logger object up, to log messages to console and to .txt file in logs/ folder.

    :return: the logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    create_new_folder('logs', config['PATH']['data'])
    fh_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler(config['PATH']['logs'])
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
