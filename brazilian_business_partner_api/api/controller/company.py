import strawberry
from fastapi import APIRouter
from strawberry.asgi import GraphQL
from strawberry.extensions import QueryDepthLimiter

from brazilian_business_partner_api.api.model import graphql_schema

company_router = APIRouter()
schema = strawberry.Schema(
    graphql_schema.Query,
    extensions=[
        QueryDepthLimiter(max_depth=10),
    ],
)
graphql_app = GraphQL(schema)
company_router.add_route("/graphql", graphql_app)
