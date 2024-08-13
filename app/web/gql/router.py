import strawberry
from strawberry.fastapi import GraphQLRouter

from app.web.gql import dummy, echo
from app.web.gql.context import Context, get_context


@strawberry.type
class Query(  # noqa: WPS215
    echo.Query,
    dummy.Query,
):
    """Main query."""


@strawberry.type
class Mutation(  # noqa: WPS215
    echo.Mutation,
    dummy.Mutation,
):
    """Main mutation."""


schema = strawberry.Schema(
    Query,
    Mutation,
)

gql_router: GraphQLRouter[Context, None] = GraphQLRouter(
    schema,
    graphiql=True,
    context_getter=get_context,
)
