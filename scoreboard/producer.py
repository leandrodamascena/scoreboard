import json
import random
from datetime import datetime
from typing import Any, Dict, List

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from data.players import MOCK_DATA  # type: ignore

logger = Logger()
metrics = Metrics()
tracer = Tracer()

kinesis_client = boto3.client("kinesis") # type: ignore[attr-defined]


@tracer.capture_method
def ingest_players(players: List[Dict[str, Any]], sdk_client = None) -> Dict[str, Any]:
    if sdk_client is None:
        sdk_client = boto3.client("kinesis")  # type: ignore[attr-defined]

    # sending data to kinesis
    logger.info("Adding records to Kinesis")
    response = sdk_client.put_records(
        Records=players, StreamName="kds_scoreboard"
    )

    # put_records can fail some records
    # creating metric with the number of successes and failed records to insert
    failed_records = response.get("FailedRecordCount", 0)
    success_records = len(response.get("Records"))

    metrics.add_metric(
        "producer_success_records", unit=MetricUnit.Count, value=success_records
    )
    metrics.add_metric(
        "producer_error_records", unit=MetricUnit.Count, value=failed_records
    )

    return {"message": "success", "FailedRecordCount": failed_records}

@logger.inject_lambda_context(correlation_id_path=correlation_paths.EVENT_BRIDGE)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    try:
        # iterating players
        players: List = []
        for data in MOCK_DATA:
            # generating a random score between 0 and 5
            score: int = random.randint(0, 5)
            data["score"] = score
            data["timestamp"] = str(datetime.now())

            # creating the kinesis record to add using put_records method
            kinesis_record: Dict[str, Any] = {
                "PartitionKey": "shardId-000000000001",
                "Data": json.dumps(data),
            }

            # appending records
            players.append(kinesis_record)
        
        return ingest_players(players, kinesis_client)
    except Exception:
        logger.exception("Unable to ingest players into the stream.")
        raise
