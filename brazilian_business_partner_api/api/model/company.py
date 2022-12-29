import pathlib
import tomllib as toml
from typing import TYPE_CHECKING, Annotated

import strawberry

import brazilian_business_partner_api
from brazilian_business_partner_api.config import config
from brazilian_business_partner_api.connect import connect


DB = connect.PostgresSingletonDB(config.DB_CONFIGS)
logger = brazilian_business_partner_api.Logger(__name__)

_TOML = toml.load(
    open(str(pathlib.Path(__file__).parent.resolve() / "queries.toml"), "rb")
)

COMPANY_QUERY = _TOML["companies"]
OPERATOR_QUERY = _TOML["operators"]

if TYPE_CHECKING:
    from .operators import Operator


@strawberry.input
class CompanyID:
    nr_cnpj: str


@strawberry.type
class Company:
    nr_cnpj: str
    nm_fantasia: str
    sg_uf: str
    operators: list[Annotated["Operator", strawberry.lazy(".operators")]] | None
