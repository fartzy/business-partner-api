import os

import click

from brazilian_business_partner_api import Logger

log_messages = []


def write_cli_log_messages():
    logger = Logger(log_name=__name__)
    for message in log_messages:
        logger.log.info(message)


def validate_forced_reload(ctx, param, value):
    exception_message = "User cancelled. The --forced-load option was chosen by the user but the user is not really 'bout that lyfe.\n"
    if value:
        if (
            input(
                "\nAre you sure you want to load all data? If you haven't loaded any data at all yet, then of course you have to choose yes.\n\n\t\t'Y' or 'y' to continue: "
            ).lower()
            == "y"
        ):
            if (
                input(
                    "\n\nAre you really serious? You will (possibly) truncate all the tables in the target database and reload EVERYTHING?\n\n\t\t'S' or 's' if you are super serious: "
                ).lower()
                == "s"
            ):
                log_messages.append(
                    f"-------------- Forced (Re)loading of all Tables!!! --------------"
                )
                return value
            else:
                raise click.ClickException(exception_message)
        else:
            raise click.ClickException(exception_message)


def log_level_option(f):
    def log_level_callback(ctx, param, value):
        os.environ["LOGLEVEL"] = value
        log_messages.append(
            f"-------------- Logging level '{value}' is set. --------------"
        )
        return value

    return click.option(
        "--log-level",
        "-ll",
        callback=log_level_callback,
        type=click.STRING,
        default="INFO",
        help="""This option will determine the level of logging for this execution of the application.
                The valid levels are:
                ERROR,
                WARNING,
                INFO,
                DEBUG,
                NOTSET""",
    )(f)


# This is set to eager to force evaluation first
def log_path_option(f):
    def log_path_callback(ctx, param, value):
        if value:
            os.environ["LOGPATH"] = value
            log_messages.append(
                f"-------------- Logging path set to '{value}'. --------------"
            )
        return value

    return click.option(
        "--log-path",
        "-lp",
        callback=log_path_callback,
        type=click.STRING,
        is_eager=True,
        default="cli.log",
        help="""This option is the whole absolute path of log file.""",
    )(f)


def forced_load_option(f):
    return click.option(
        "--forced-load",
        "-fl",
        callback=validate_forced_reload,
        is_flag=True,
        default=False,
        help="This option is so the user can reload all of the data if they so choose (takes like 30-35 minutes).",
    )(f)


def config_path_option(f):
    def config_path_callback(ctx, param, value):
        log_messages.append(
            f"-------------- Database config file path is set to '{value}' --------------"
        )
        return value

    return click.option(
        "--config-path",
        "-c",
        callback=config_path_callback,
        type=click.Path(exists=True),
        required=True,
        help="This option is the path of the config file, which is needed for database connectivity.",
    )(f)


def sample_size_option(f):
    def sample_size_callback(ctx, param, value):
        if value > 0:
            log_messages.append(
                f"-------------- SAMPLE SIZE set to '{value}' --------------"
            )
        return value

    return click.option(
        "--sample-size",
        "-s",
        callback=sample_size_callback,
        type=click.INT,
        default=0,
        help="This option when set will determine the amount of records that will be retrived from the CSV file.",
    )(f)


def csv_file_path_option(f):
    def csv_file_path_callback(ctx, param, value):
        if value:
            log_messages.append(
                f"-------------- CSV FILE PATH set to '{value}' --------------"
            )
        return value

    return click.option(
        "--csv-file-path",
        "-fp",
        callback=csv_file_path_callback,
        type=click.Path(exists=True),
        required=True,
        help="This option can be given to set the location of the raw CSV file of Brazilian companies.",
    )(f)


def log_config_file_path_option(f):
    def log_config_file_path_callback(ctx, param, value):
        if value:
            log_messages.append(
                f"-------------- LOG CONFIG FILE PATH is set to '{value}' --------------"
            )
        return value

    return click.option(
        "--log-config-file-path",
        "-lcf",
        callback=log_config_file_path_callback,
        type=click.STRING,
        required=False,
        help="This option is given to allow the user to set the log configuration with an .ini file",
    )(f)
