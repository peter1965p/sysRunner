import logging

class LogEngine:
    def __init__(self):
        self.logger = logging.getLogger("SysRunner")
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        self.logger.addHandler(handler)

        self.ui_callback = None

    def set_ui_callback(self, fn):
        self.ui_callback = fn

    def info(self, msg):
        self.logger.info(msg)
        if self.ui_callback:
            self.ui_callback(msg)

    def error(self, msg):
        self.logger.error(msg)
        if self.ui_callback:
            self.ui_callback(msg)

    def warn(self, msg):
        self.logger.warning(msg)
        if self.ui_callback:
            self.ui_callback(msg)
