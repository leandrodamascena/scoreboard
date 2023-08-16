from datetime import datetime
from typing import Dict

import boto3
import schemas.player_schema as schemas  # type: ignore
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    ExceptionInfo,
    FailureResponse,
    process_partial_response,
)
from aws_lambda_powertools.utilities.batch.types import PartialItemFailureResponse
from aws_lambda_powertools.utilities.data_classes.kinesis_stream_event import (
    KinesisStreamRecord,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import SchemaValidationError, validate

tracer = Tracer()
logger = Logger()
metrics = Metrics()
dynamodb_client = boto3.client("dynamodb") # type: ignore[attr-defined]


# Custom BatchProcessor class to handle errors and create metrics for error tracking
class BatchProcessorWithMetrics(BatchProcessor):
    def failure_handler(
        self, record: KinesisStreamRecord, exception: ExceptionInfo
    ) -> FailureResponse:
        metrics.add_metric(
            name="consumer_records_failure", unit=MetricUnit.Count, value=1
        )

        logger.exception(
            "error processing a record",
            exception=exception,
            kinesis_sequence=record.kinesis.sequence_number,
        )
        return super().failure_handler(record, exception)


processor = BatchProcessorWithMetrics(event_type=EventType.KinesisDataStreams)


@tracer.capture_method
def record_handler(record: KinesisStreamRecord) -> None:
    # Getting the players' details from the Kinesis data as JSON
    kinesis_record: dict = record.kinesis.data_as_json()

    try:
        # Validating player data against the player schema
        # See https://awslabs.github.io/aws-lambda-powertools-python/2.15.0/utilities/validation/#validate-function
        validate(event=kinesis_record, schema=schemas.PLAYER_SCHEMA)

        # Extracting player attributes
        player_name = kinesis_record.get("player_name")
        timestamp = kinesis_record.get("timestamp")
        player_country = kinesis_record.get("player_country")
        player_os = kinesis_record.get("player_os")
        player_level = kinesis_record.get("player_level")
        score = kinesis_record.get("score")
        # adding 1 day to expire ttl
        expiration = int(datetime.now().timestamp()) + 86400

        item = {
            "player_name": {"S": player_name},
            "timestamp": {"S": str(timestamp)},
            "player_country": {"S": player_country},
            "player_os": {"S": player_os},
            "player_level": {"S": player_level},
            "score": {"N": str(score)},
            "expiration": {"N": str(expiration)},
        }

        # Adding data to DynamoDB
        dynamodb_client.put_item(TableName="ScoreboardRawData", Item=item)
    except SchemaValidationError as exc:
        # Handle schema validation error
        logger.error("Player data validation failed", error=str(exc))
        raise SchemaValidationError(f"Player data validation failed {str(exc)}")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(
    event: Dict, context: LambdaContext
) -> PartialItemFailureResponse:
    # Adding metrics to track the number of records to be processed at this time
    metrics.add_metric(
        name="consumer_records_to_process",
        unit=MetricUnit.Count,
        value=len(event.get("Records", [])),
    )

    # processing messages
    return process_partial_response(
        event=event, record_handler=record_handler, processor=processor, context=context
    )
