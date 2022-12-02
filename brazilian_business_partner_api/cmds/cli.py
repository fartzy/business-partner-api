import click
import click_log
from gettext import gettext as _

from brazilian_business_partner_api.cmds.dataload_cli import dataload
from brazilian_business_partner_api.cmds.apiservice_cli import api


@click.group()
def cli():
    pass


cli = click.CommandCollection(sources=[dataload, api])

if __name__ == "__main__":
    cli()
