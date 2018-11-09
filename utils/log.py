import logging


def set_logger_up():
    """ Sets the logger object up, to log messages to console and to .txt file in logs/ folder.

    :return: the logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    fh_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler(
        '/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/logs/logs.txt')
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


logger = set_logger_up()
