import boto3
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from shared.dynamodb import build_and_query_dynamodb

tracer = Tracer()
logger = Logger()
app = APIGatewayRestResolver()

dynamodb_client = boto3.client("dynamodb")


@app.get("/score")
@tracer.capture_method
def get_score():
    order_by: str = app.current_event.get_query_string_value(
        name="order", default_value="all"
    )
    filter: str = app.current_event.get_query_string_value(
        name="filter", default_value=""
    )

    statement = build_and_query_dynamodb(dynamodb_client, order_by, filter)
    return statement


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
