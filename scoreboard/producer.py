import json
import random
from datetime import datetime
from typing import Any, Dict, List

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from data.players import MOCK_DATA

logger = Logger()
metrics = Metrics()
tracer = Tracer()

kinesis_client = boto3.client("kinesis")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
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
                "PartitionKey": f"shardId-00000000000{score}",
                "Data": json.dumps(data),
            }

            # appending records
            players.append(kinesis_record)

        # sending data to kinesis
        logger.info("Adding records to Kinesis")
        response = kinesis_client.put_records(
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

    except Exception as exc:
        logger.exception(f"An error occurred: {exc}")
        raise
