import pathlib
import tomllib as toml
from typing import TYPE_CHECKING, Annotated

import strawberry

import brazilian_business_partner_api.api.model
from brazilian_business_partner_api.config import config
from brazilian_business_partner_api.connect import connect


DB = connect.PostgresSingletonDB(config.DB_CONFIGS)

_TOML = toml.load(
    open(str(pathlib.Path(__file__).parent.resolve() / "queries.toml"), "rb")
)

COMPANY_QUERY = _TOML["companies"]
OPERATOR_QUERY = _TOML["operators"]

if TYPE_CHECKING:
    from .company import Company


@strawberry.input
class OperatorKey:
    key: str


@strawberry.type
class Operator:
    operator_key: str
    in_cpf_cnpj: str
    nm_socio: str
    companies: list[Annotated["Company", strawberry.lazy(".company")]] | None
