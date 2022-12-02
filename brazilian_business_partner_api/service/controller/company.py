import strawberry
from fastapi import APIRouter
from strawberry.asgi import GraphQL

from brazilian_business_partner_api.service.model import company

company_router = APIRouter()
schema = strawberry.Schema(company.Query)
graphql_app = GraphQL(schema)
company_router.add_route("/graphql", graphql_app)
