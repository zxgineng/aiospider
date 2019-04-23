import logging
import os

logger = logging.getLogger("mylogger")


def init_log(spider):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    save_dir = os.path.join(log_dir, spider.__class__.__name__)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    if spider.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%d %b %Y %H:%M:%S')
    hdlr = logging.StreamHandler()
    hdlr.setFormatter(formatter)
    hdlr.setLevel(logging.DEBUG)
    logger.addHandler(hdlr)

    hdlr = logging.FileHandler(os.path.join(save_dir, "log.txt"))
    hdlr.setFormatter(formatter)
    hdlr.setLevel(logging.ERROR)
    logger.addHandler(hdlr)
