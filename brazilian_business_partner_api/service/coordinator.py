import pathlib

import brazilian_business_partner_api
from brazilian_business_partner_api.service import apprunner


class APICoordinator:
    """Class for coordinating the instantiation of the API service
    Args:
        None
    Attributes:
        None
    """

    logger = None

    @classmethod
    def get_logger(cls):
        if cls.logger is None:
            cls.logger = brazilian_business_partner_api.Logger(log_name=__name__)
        return cls.logger

    @staticmethod
    def run(
        log_level: str,
        log_path: str,
        config_file_path: pathlib.Path,
    ):
        """This function starts the service

        Args:
            log_level (str) : log level
            log_path (str) : log path
            config_file_path (Path) : The full path of the config file

        Returns:
            None
        """

        current_path = pathlib.Path(__file__).parent.resolve()
        APICoordinator.get_logger().log.info(
            f"Executing `braz-bpa-cli api` and the APICoordinator.run() method from the python file '{current_path}'..."
        )

        runner = apprunner.AppRunner(config_file_path)
        runner.run()
