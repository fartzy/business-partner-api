import datetime
import logging
import pathlib
import tomllib as toml
from typing import Optional

import strawberry
from strawberry.types import Info

import brazilian_business_partner_api
from brazilian_business_partner_api.config import config
from brazilian_business_partner_api.connect import connect
from brazilian_business_partner_api.api.model.company import Company, CompanyID
from brazilian_business_partner_api.api.model.operators import Operator, OperatorKey

DB = connect.PostgresSingletonDB(config.DB_CONFIGS)
logger = brazilian_business_partner_api.Logger(log_name=__name__)


_TOML = toml.load(
    open(str(pathlib.Path(__file__).parent.resolve() / "queries.toml"), "rb")
)
MAX_DEPTH = 10 
COMPANY_QUERY = _TOML["companies"]
OPERATOR_QUERY = _TOML["operators"]

# @strawberry.type
# class Query:
#     @strawberry.field
#     def company(self, companyId: company.CompanyID = strawberry.UNSET) -> company.Company:
#         if companyId is strawberry.UNSET:
#             raise Exception("You need to give the nr_cnpj")

#         operators = []
#         operator_companies = []
#         nr_cnpj = ""
#         nm_fantasia = ""
#         sg_uf = ""
#         for row in DB.execute(
#             logger,COMPANY_QUERY.format(nr_cnpj=companyId.nr_cnpj),
#         ).fetchall():
#             nr_cnpj = row[0]
#             nm_fantasia = row[1]
#             sg_uf = row[2]

#             for _nr_cnpj,_nm_fantasia,_sg_uf in zip(row[6], row[7], row[8]):
#                 operator_companies.append(company.Company(nr_cnpj=_nr_cnpj, nm_fantasia=_nm_fantasia,sg_uf=_sg_uf))

#             operators.append(
#                 operator.Operator(
#                     operator_key=row[3],
#                     in_cpf_cnpj=row[4],
#                     nm_socio=row[5],
#                     companies=operator_companies
#                 )
#             )

#         return company.Company(
#             nr_cnpj=nr_cnpj, nm_fantasia=nm_fantasia, sg_uf=sg_uf, operators=operators
#         )
class Resolvers:
    @staticmethod
    def company(companyId: CompanyID = strawberry.UNSET, depth: int = 0) -> Company:
        if companyId is strawberry.UNSET:
            raise Exception("You need to give the nr_cnpj")

        operators = []
        nr_cnpj = ""
        nm_fantasia = ""
        sg_uf = ""
        for row in DB.execute(
            logger,
            COMPANY_QUERY.format(nr_cnpj=companyId.nr_cnpj),
        ).fetchall():
            nr_cnpj = row[0]
            nm_fantasia = row[1]
            sg_uf = row[2]
            if depth == MAX_DEPTH:
                return Company(nr_cnpj=nr_cnpj, nm_fantasia=nm_fantasia, sg_uf=sg_uf, operators=None)

            logger.log.debug(f"Operator array_agg() database value (row[3]) = {row[3]}")

            for ind, _operator_key in enumerate(row[3]):
                logger.log.debug(
                    f"Iterating through the array_agg() result - value {ind} for _operator_key = {_operator_key}"
                )
                operators.append(Resolvers.operator(OperatorKey(key=_operator_key), depth=depth+1))


        return Company(
            nr_cnpj=nr_cnpj, nm_fantasia=nm_fantasia, sg_uf=sg_uf, operators=operators
        )

    def operator(operatorKey: OperatorKey = strawberry.UNSET, depth: int = 0) -> Operator:
        if operatorKey is strawberry.UNSET:
            raise Exception("You need to give the operator key")

        operator_key = ""
        in_cpf_cnpj = ""
        nm_socio = ""
        companies = []
        for row in DB.execute(
            logger,
            OPERATOR_QUERY.format(operator_key=operatorKey.key),
        ).fetchall():
            operator_key = row[0]
            in_cpf_cnpj = row[1]
            nm_socio = row[2]
            if depth == MAX_DEPTH:
                return Operator(operator_key=operator_key, in_cpf_cnpj=in_cpf_cnpj, nm_socio=nm_socio, companies=None)

            logger.log.debug(f"Company array_agg() database value (row[3]) = {row[3]}")
            for ind, _nr_cnpj in enumerate(row[3]):
                logger.log.debug(
                    f"Iterating through the array_agg() result - value {ind} for _nr_cnpj = {_nr_cnpj}"
                )
                companies.append(Resolvers.company(CompanyID(nr_cnpj=_nr_cnpj), depth=depth+1))

        return Operator(
            operator_key=operator_key,
            in_cpf_cnpj=in_cpf_cnpj,
            nm_socio=nm_socio,
            companies=companies,
        )


@strawberry.type
class Query:
    @strawberry.field
    def company(
        self,
        companyId: CompanyID = strawberry.UNSET,
    ) -> Company:
        return Resolvers.company(companyId)

    @strawberry.field
    def operator(
        self,
        operatorKey: OperatorKey = strawberry.UNSET,
    ) -> Operator:
        return Resolvers.operator(operatorKey)

    # @strawberry.field
    # def operator(
    #     self,
    #     operatorKey: OperatorKey = strawberry.UNSET,
    # ) -> Operator:
    #     if operatorKey is strawberry.UNSET:
    #         raise Exception("You need to give the operator key")

    #     operator_key = ""
    #     in_cpf_cnpj = ""
    #     nm_socio = ""
    #     companies = []
    #     for row in DB.execute(
    #         logger,
    #         "".format(operator_key=operatorKey.key),
    #     ).fetchall():
    #         operator_key = row[0]
    #         in_cpf_cnpj = row[1]
    #         nm_socio = row[2]
    #         companies.append(
    #             Company(
    #                 nr_cnpj=row[3],
    #                 nm_fantasia=row[4],
    #                 sg_uf=row[5],
    #             )
    #         )

    #     return Operator(
    #         operator_key=operator_key,
    #         in_cpf_cnpj=in_cpf_cnpj,
    #         nm_socio=nm_socio,
    #         companies=companies,
    #     )
