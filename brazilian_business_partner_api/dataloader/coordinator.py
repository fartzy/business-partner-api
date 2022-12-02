import pathlib

import brazilian_business_partner_api
from brazilian_business_partner_api.config import config
from brazilian_business_partner_api.dataloader import importer, transformer


class ELTCoordinator:
    """Class for coordinating the entire data pipelines including import and transform
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
    def load(
        log_level: str,
        log_path: str,
        config_file_path: pathlib.Path,
        csv_file_path: str,
        load_raw_data: bool,
        sample_size: int = 0,
    ):
        """This function does all the logic for loading data

        Args:
            log_level (str) : log level
            log_path (str) : log path
            config_file_path (Path) : The full path of the config file
            csv_file_path (str) : The full path of the csv file
            load_raw_data (bool): The flag coming from the user to force loading of raw data
            sample_size (int): When doing a sample ingestion, the user provides this as the amount of rows to use

        Returns:
            None
        """
        current_path = pathlib.Path(__file__).parent.resolve()
        ELTCoordinator.get_logger().log.info(
            f"Executing `braz-bpa-cli dataload` and the ELTCoordinator.load() method from the python file '{current_path}'..."
        )

        _importer = importer.Importer(
            csv_file_path, config_file_path, config.DB_CONFIGS
        )
        _importer.load(load_raw_data, sample_size)

    @staticmethod
    def transform(
        log_level: str,
        log_path: str,
        config_file_path: pathlib.Path,
        transform_data: bool,
        sample_size: int = 0,
    ):
        """This function does all the logic for loading data

        Args:
            log_level (str) : log level
            log_path (str) : log path
            config_file_path (Path) : The full path of the config file
            load_data (bool): The flag coming from the user to force transforming of the data
            sample_size (int): When doing a sample ingestion, the user provides this as the amount of rows to use

        Returns:
            None
        """
        current_path = pathlib.Path(__file__).parent.resolve()
        ELTCoordinator.get_logger().log.info(
            f"Executing `braz-bpa-cli dataload` and the ELTCoordinator.transform() method from the python file '{current_path}'..."
        )

        _transformer = transformer.Transformer(config_file_path, config.DB_CONFIGS)
        _transformer.transform(transform_data, sample_size)
