import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.batch.types import PartialItemFailureResponse
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBRecord,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from typing import Dict
processor = BatchProcessor(event_type=EventType.DynamoDBStreams)
tracer = Tracer()
logger = Logger()
metrics = Metrics()

dynamodb_client = boto3.client("dynamodb") # type: ignore[attr-defined]
TABLE_NAME = "ScoreboardSummedUpData"  # TODO: Use env var


@tracer.capture_method
def record_handler(record: DynamoDBRecord):
    if record.dynamodb and record.dynamodb.new_image:
        new_image = record.dynamodb.new_image
        keys: Dict = record.dynamodb.keys # type: ignore[assignment]

        player_name = keys.get("player_name")
        player_country = new_image.get("player_country")
        player_os = new_image.get("player_os")
        player_level = new_image.get("player_level")
        score = new_image.get("score")

        response = dynamodb_client.get_item(
            TableName=TABLE_NAME, Key={"player_name": {"S": player_name}}
        )

        if "Item" in response:
            # Player record already exists, update the score
            existing_score = int(response["Item"]["score"]["N"])
            updated_score = existing_score + score
            dynamodb_client.update_item(
                TableName=TABLE_NAME,
                Key={"player_name": {"S": player_name}},
                UpdateExpression="SET score = :score",
                ExpressionAttributeValues={":score": {"N": str(updated_score)}},
            )
            logger.info(f"Score updated for player '{player_name}'.")
        else:
            # Create a new player record
            item = {
                "player_name": {"S": player_name},
                "player_country": {"S": player_country},
                "player_os": {"S": player_os},
                "player_level": {"S": player_level},
                "score": {"N": str(score)},
            }
            dynamodb_client.put_item(TableName=TABLE_NAME, Item=item)
            logger.info(f"New player record created for '{player_name}'.")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context: LambdaContext) -> PartialItemFailureResponse:
    # Adding metrics to track the number of records to be processed at this time
    metrics.add_metric(
        name="summarize_records_to_process",
        unit=MetricUnit.Count,
        value=len(event.get("Records", [])),
    )
    return process_partial_response(
        event=event, record_handler=record_handler, processor=processor, context=context
    )
