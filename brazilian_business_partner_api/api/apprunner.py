import pathlib
import uvicorn

import brazilian_business_partner_api
from brazilian_business_partner_api.api import app
from brazilian_business_partner_api.connect import connect


class AppRunner:
    def __init__(self, config_file_path: str, log_path: str = None):
        if log_path:
            self.log_path = log_path
        self.url = "127.0.0.1"
        self.port = 8000
        self.logger = (
            brazilian_business_partner_api.Logger(
                log_name=__name__, log_path=self.log_path
            )
            if log_path
            else brazilian_business_partner_api.Logger(log_name=__name__)
        )
        self.subprocess_cmd = [
            "uvicorn",
            "app:app",
            "--host",
            self.url,
            "--port",
            self.port,
        ]

    def run(self):
        self.logger.log.debug("Starting the uvicorn server...")
        uvicorn.run(
            "brazilian_business_partner_api.api.app:app",
            host=self.url,
            port=self.port,
            log_config=str(pathlib.Path(__file__).parent.parent / "config/log.ini"),
        )
