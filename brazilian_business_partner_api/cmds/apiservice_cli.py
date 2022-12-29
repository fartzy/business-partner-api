import pathlib

import click

from brazilian_business_partner_api.cmds.config import (
    config_path_option,
    log_level_option,
    log_path_option,
    write_cli_log_messages,
)
from brazilian_business_partner_api.api.coordinator import APICoordinator


@click.group()
def api():
    pass


@api.command("api")
@log_level_option
@log_path_option
@config_path_option
def dataload_cli(
    log_level,
    log_path,
    config_path,
):
    write_cli_log_messages()

    APICoordinator.run(
        log_level=log_level,
        log_path=log_path,
        config_file_path=pathlib.Path(config_path),
    )
