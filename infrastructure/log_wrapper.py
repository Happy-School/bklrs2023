import logging
import os
from datetime import datetime

LOG_FORMAT = "%(asctime)s %(message)s"
DEFAULT_LEVEL = logging.DEBUG

class LogWrapper:
    PATH = './logs'

    def __init__(self, name, add_file_handler=True):
        self.name = name
        self.filename = self.construct_log_filename()

        self.logger = logging.getLogger(name)
        self.logger.setLevel(DEFAULT_LEVEL)

        if add_file_handler:
            self.create_directory_if_needed()
            self.add_file_handler_to_logger()

        self.logger.info(f"LogWrapper initialized: {self.filename}")

    def construct_log_filename(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"{LogWrapper.PATH}/{self.name}_{date_str}.log"

    def create_directory_if_needed(self):
        if not os.path.exists(LogWrapper.PATH):
            os.makedirs(LogWrapper.PATH)

    def add_file_handler_to_logger(self):
        mode = 'a' if os.path.exists(self.filename) else 'w'
        file_handler = logging.FileHandler(self.filename, mode=mode)
        formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)











