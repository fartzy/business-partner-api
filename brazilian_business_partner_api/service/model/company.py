import datetime
import logging
import pathlib
import tomllib as toml
from typing import Optional

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

@strawberry.input
class CompanyID:
    nr_cnpj: str

@strawberry.input
class OperatorKey:
    key: str


@strawberry.type
class QualificacaoSocio:
    cd_qualificacao_socio: Optional[str]
    ds_qualificacao_socio: Optional[str] = strawberry.UNSET

@strawberry.type
class OperatorCompany:
    nr_cnpj: str
    nm_fantasia: str
    sg_uf: str

@strawberry.type
class Operator:
    operator_key: str
    in_cpf_cnpj: str
    nm_socio: str
    companies: Optional[list[OperatorCompany]]


@strawberry.type
class Company:
    nr_cnpj: str
    nm_fantasia: str
    sg_uf: str
    operators: Optional[list[Operator]]


@strawberry.type
class Query:
    @strawberry.field
    def company(self, companyId: CompanyID = strawberry.UNSET) -> Company:
        if companyId is strawberry.UNSET:
            raise Exception("You need to give the nr_cnpj")

        operators = []
        operator_companies = []
        nr_cnpj = ""
        nm_fantasia = ""
        sg_uf = ""
        for row in DB.execute(
            logger,COMPANY_QUERY.format(nr_cnpj=companyId.nr_cnpj),
        ).fetchall():
            nr_cnpj = row[0]
            nm_fantasia = row[1]
            sg_uf = row[2]

            for _nr_cnpj,_nm_fantasia,_sg_uf in zip(row[6], row[7], row[8]):
                operator_companies.append(OperatorCompany(nr_cnpj=_nr_cnpj, nm_fantasia=_nm_fantasia,sg_uf=_sg_uf))

            operators.append(
                Operator(
                    operator_key=row[3],
                    in_cpf_cnpj=row[4],
                    nm_socio=row[5],
                    companies=operator_companies
                )
            )

        return Company(
            nr_cnpj=nr_cnpj, nm_fantasia=nm_fantasia, sg_uf=sg_uf, operators=operators
        )

    @strawberry.field
    def operator(self, operatorKey: OperatorKey = strawberry.UNSET) -> Operator:
        if operatorKey is strawberry.UNSET:
            raise Exception("You need to give the operator key")

        operator_key = ""
        in_cpf_cnpj = ""
        nm_socio = ""
        companies = []
        for row in DB.execute(
            logger,
            "".format(operator_key=operatorKey.key),
        ).fetchall():
            operator_key = row[0]
            in_cpf_cnpj = row[1]
            nm_socio = row[2]
            companies.append(
                OperatorCompany(
                    nr_cnpj=row[3],
                    nm_fantasia=row[4],
                    sg_uf=row[5],
                )
            )

        return Operator(
            operator_key=operator_key, in_cpf_cnpj=in_cpf_cnpj, nm_socio=nm_socio, companies=companies
        )