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

# Module constants
DEFAULT_MAX_DEPTH = 3

_TOML = toml.load(
    open(str(pathlib.Path(__file__).parent.resolve() / "queries.toml"), "rb")
)

COMPANY_QUERY = _TOML["companies"]
OPERATOR_QUERY = _TOML["operators"]
COMPANY_BASE_QUERY = _TOML["company_base"]
OPERATOR_BASE_QUERY = _TOML["operator_base"]
COMPANY_OPERATORS_QUERY = _TOML["company_operators"]
OPERATOR_COMPANIES_QUERY = _TOML["operator_companies"]
CONNECTED_COMPANIES_QUERY = _TOML["connected_companies"]

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
class Company:
    nr_cnpj: str
    nm_fantasia: str
    sg_uf: str

    @strawberry.field
    def operators(
        self, 
        info: strawberry.Info,
        max_depth: Optional[int] = DEFAULT_MAX_DEPTH
    ) -> Optional[list["Operator"]]:
        """Get operators for this company with depth control"""
        current_depth = getattr(info.context, 'query_depth', 0)
        if current_depth >= (max_depth or DEFAULT_MAX_DEPTH):
            return []
            
        # Set context for nested queries
        info.context.query_depth = current_depth + 1
        
        operators = []
        try:
            result = DB.execute(logger, COMPANY_OPERATORS_QUERY.format(nr_cnpj=self.nr_cnpj)).fetchall()
            for row in result:
                operators.append(Operator(
                    operator_key=row[0],
                    in_cpf_cnpj=row[1],
                    nm_socio=row[2]
                ))
        except Exception as e:
            logger.error(f"Error fetching operators for company {self.nr_cnpj}: {e}")
            return []
        finally:
            # Reset context depth
            info.context.query_depth = current_depth
            
        return operators

@strawberry.type
class Operator:
    operator_key: str
    in_cpf_cnpj: str
    nm_socio: str

    @strawberry.field
    def companies(
        self, 
        info: strawberry.Info,
        max_depth: Optional[int] = DEFAULT_MAX_DEPTH
    ) -> Optional[list[Company]]:
        """Get companies for this operator with depth control"""
        current_depth = getattr(info.context, 'query_depth', 0)
        if current_depth >= (max_depth or DEFAULT_MAX_DEPTH):
            return []
            
        # Set context for nested queries
        info.context.query_depth = current_depth + 1
        
        companies = []
        try:
            result = DB.execute(logger, OPERATOR_COMPANIES_QUERY.format(operator_key=self.operator_key)).fetchall()
            for row in result:
                companies.append(Company(
                    nr_cnpj=row[0],
                    nm_fantasia=row[1],
                    sg_uf=row[2]
                ))
        except Exception as e:
            logger.error(f"Error fetching companies for operator {self.operator_key}: {e}")
            return []
        finally:
            # Reset context depth
            info.context.query_depth = current_depth
            
        return companies


@strawberry.type
class Query:
    @strawberry.field
    def company(
        self, 
        companyId: CompanyID = strawberry.UNSET,
        info: strawberry.Info = strawberry.UNSET
    ) -> Optional[Company]:
        """Get a company by CNPJ number"""
        if companyId is strawberry.UNSET:
            raise Exception("You need to provide nr_cnpj")

        # Initialize query depth context
        if not hasattr(info.context, 'query_depth'):
            info.context.query_depth = 0

        try:
            result = DB.execute(logger, COMPANY_BASE_QUERY.format(nr_cnpj=companyId.nr_cnpj)).fetchone()
            if not result:
                return None
                
            return Company(
                nr_cnpj=result[0],
                nm_fantasia=result[1],
                sg_uf=result[2]
            )
        except Exception as e:
            logger.error(f"Error fetching company {companyId.nr_cnpj}: {e}")
            raise Exception(f"Failed to fetch company: {str(e)}")

    @strawberry.field
    def operator(
        self, 
        operatorKey: OperatorKey = strawberry.UNSET,
        info: strawberry.Info = strawberry.UNSET
    ) -> Optional[Operator]:
        """Get an operator by operator key"""
        if operatorKey is strawberry.UNSET:
            raise Exception("You need to provide operator key")

        # Initialize query depth context
        if not hasattr(info.context, 'query_depth'):
            info.context.query_depth = 0

        try:
            result = DB.execute(logger, OPERATOR_BASE_QUERY.format(operator_key=operatorKey.key)).fetchone()
            if not result:
                return None
                
            return Operator(
                operator_key=result[0],
                in_cpf_cnpj=result[1],
                nm_socio=result[2]
            )
        except Exception as e:
            logger.error(f"Error fetching operator {operatorKey.key}: {e}")
            raise Exception(f"Failed to fetch operator: {str(e)}")
            
    @strawberry.field 
    def connected_companies(
        self,
        companyId: CompanyID = strawberry.UNSET,
        max_depth: Optional[int] = 2
    ) -> Optional[list[Company]]:
        """Get all companies connected through shared operators"""
        if companyId is strawberry.UNSET:
            raise Exception("You need to provide nr_cnpj")
            
        try:
            result = DB.execute(
                logger, 
                CONNECTED_COMPANIES_QUERY.format(
                    nr_cnpj=companyId.nr_cnpj, 
                    max_depth=max_depth or 2
                )
            ).fetchall()
            companies = []
            for row in result:
                companies.append(Company(
                    nr_cnpj=row[0],
                    nm_fantasia=row[1], 
                    sg_uf=row[2]
                ))
            return companies
        except Exception as e:
            logger.error(f"Error fetching connected companies for {companyId.nr_cnpj}: {e}")
            return []