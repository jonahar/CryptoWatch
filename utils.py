import logging
import os
import sys
from logging import Logger

from config import LOGFILE


def setup_logging(
    logger_name: str = None,
    console: bool = True,
    filename: str = None,
    fmt: str = None
) -> Logger:
    """
    setup a logger with a specific format and possibly console/file handlers
    
    :param logger_name: the logger to setup. If none, setup the root logger
    :param console: booleans indicating whether to log to standard output with level INFO
    :param filename: log file. If not None, log to this file with level DEBUG
    :param fmt: format for log messages. if None, a default format is used
    :return: the logger that was set-up
    """
    if fmt is None:
        fmt = "%(asctime)s: %(levelname)s: %(module)s: %(funcName)s: %(message)s"
    formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # the logger doesn't filter anything
    
    # console handler
    if console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)
    
    # file handler
    if filename:
        logdir = os.path.dirname(filename)
        os.makedirs(logdir, exist_ok=True)  # create all directories in the path, if not exist
        fh = logging.FileHandler(filename)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    
    return logger


logger = setup_logging(logger_name="cryptowatch", console=False, filename=LOGFILE)
