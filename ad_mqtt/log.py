import logging


def log_setup(log_level, log_screen, log_file):
    if log_screen:
        log_handler = logging.StreamHandler()
    if log_file:
        log_handler = logging.handlers.WatchedFileHandler(log_file)

    log_names = ["ad_mqtt"]

    for name in log_names:
        logging.basicConfig(format='%(asctime)s %(message)s')
        log = logging.getLogger(name)
        log.setLevel(logging.getLevelName(log_level))

        if log_screen or log_file:
            log.addHandler(log_handler)
