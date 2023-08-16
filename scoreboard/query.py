import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from shared.dynamodb import build_and_query_dynamodb # type: ignore[import]

tracer = Tracer()
logger = Logger()
cors_config = CORSConfig(allow_origin="*", allow_headers=["x-api-key"], max_age=300)
app = APIGatewayRestResolver(cors=cors_config)

dynamodb_client = boto3.client("dynamodb")  # type: ignore[attr-defined]


@app.get("/score")
@tracer.capture_method
def get_score():
    order_by: str = app.current_event.get_query_string_value(
        name="order", default_value="all"
    )
    order_filter: str = app.current_event.get_query_string_value(
        name="order_filter", default_value=""
    )

    return build_and_query_dynamodb(dynamodb_client, order_by, order_filter)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
