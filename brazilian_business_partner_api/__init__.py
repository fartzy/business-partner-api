import logging
import logging.config
import os
import pathlib


class Logger:
    def __init__(
        self,
        log_name: str,
        log_level: None | str = None,
        log_path: None | str = None,
        log_config_file=str(pathlib.Path(__file__).parent / "config/log.ini"),
    ):
        logging.config.fileConfig(log_config_file, disable_existing_loggers=False)
        if not log_level:
            self.log_level = os.environ.get("LOGLEVEL", "INFO")
        else:
            self.log_level = log_level

        if not log_path:
            self.log_path = os.environ.get("LOGPATH", "app.log")
        else:
            self.log_path = log_path

        self.handler = logging.FileHandler(
            self.log_path,
            mode="a",
        )
        self.formatter = logging.Formatter(
            "[%(asctime)s.%(msecs)d] %(name)-12s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.handler.setLevel(self.log_level)
        self.handler.name
        self.handler.setFormatter(self.formatter)
        self.log = logging.getLogger(log_name)
        self.log.addHandler(self.handler)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
