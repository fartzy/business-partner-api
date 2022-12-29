import datetime
import logging
import pathlib
import tomllib as toml
from typing import Optional

import strawberry

import brazilian_business_partner_api
from brazilian_business_partner_api.config import config
from brazilian_business_partner_api.connect import connect
from brazilian_business_partner_api.service.model import company, operator

DB = connect.PostgresSingletonDB(config.DB_CONFIGS)
logger = brazilian_business_partner_api.Logger(__name__)

_TOML = toml.load(
    open(str(pathlib.Path(__file__).parent.resolve() / "queries.toml"), "rb")
)

COMPANY_QUERY = _TOML["companies"]
OPERATOR_QUERY = _TOML["operators"]


@strawberry.input
class OperatorKey:
    key: str

@strawberry.type
class Operator:
    operator_key: str
    in_cpf_cnpj: str
    nm_socio: str
    companies: Optional[list[company.Company]]