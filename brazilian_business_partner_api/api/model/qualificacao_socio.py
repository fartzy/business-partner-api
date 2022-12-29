import datetime
import logging
import pathlib
import tomllib as toml

import strawberry

import brazilian_business_partner_api
from brazilian_business_partner_api.config import config
from brazilian_business_partner_api.connect import connect


DB = connect.PostgresSingletonDB(config.DB_CONFIGS)
logger = brazilian_business_partner_api.Logger(__name__)


@strawberry.type
class QualificacaoSocio:
    cd_qualificacao_socio: str | None
    ds_qualificacao_socio: str | None = strawberry.UNSET
