import pathlib

import click

from brazilian_business_partner_api.cmds.config import (
    config_path_option,
    csv_file_path_option,
    log_level_option,
    log_path_option,
    sample_size_option,
    forced_load_option,
    write_cli_log_messages,
)
from brazilian_business_partner_api.dataloader.coordinator import ELTCoordinator


@click.group()
def dataload():
    pass


@dataload.command("dataload")
@log_level_option
@log_path_option
@config_path_option
@csv_file_path_option
@forced_load_option
@sample_size_option
def dataload_cli(
    log_level,
    log_path,
    config_path,
    csv_file_path,
    forced_load,
    sample_size,
):
    write_cli_log_messages()

    ELTCoordinator.load(
        log_level=log_level,
        log_path=log_path,
        config_file_path=pathlib.Path(config_path),
        csv_file_path=csv_file_path,
        load_raw_data=forced_load,
        sample_size=sample_size,
    )

    ELTCoordinator.transform(
        log_level=log_level,
        log_path=log_path,
        config_file_path=pathlib.Path(config_path),
        transform_data=forced_load,
        sample_size=sample_size,
    )
