import logging
from io import StringIO as StringBuffer

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(threadName)s [%(levelname)s] %(message)s")


def log_init():
    # File log handler
    file_handler = logging.FileHandler('/tmp/conf_manager.log', mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    log.addHandler(file_handler)

    # Console log handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    log.addHandler(console_handler)


class Log2Variable:
    log_capture_string = StringBuffer()

    @classmethod
    def init(cls):
        cls.log_capture_string = StringBuffer()
        ch = logging.StreamHandler(cls.log_capture_string)
        second_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        ch.setFormatter(second_formatter)
        log.addHandler(ch)

    @classmethod
    def result(cls):
        return cls.log_capture_string.getvalue()


log.debug("Logger initiated")