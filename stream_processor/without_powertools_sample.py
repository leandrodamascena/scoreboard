from datetime import datetime
from typing import Any
import logging
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import base64

# configuring xray
xray_recorder.configure(service='ScoreboardWithoutPT')
patch_all()

import boto3
dynamodb_client = boto3.client("dynamodb")
cloudwatch_client = boto3.client("cloudwatch")

# configuring Logger
logger = logging.getLogger('processor_without_powertools')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setLevel(logging.INFO)
stream_output = logging.StreamHandler()
logger.addHandler(stream_output)


def process_message(record: dict) -> None:
    # Getting the players' details from the Kinesis data as JSON
    kinesis_record = base64.b64decode(record["kinesis"]["data"]).decode("UTF-8")

    try:
        # Extracting player attributes
        player_name = kinesis_record.get("player_name", None)
        timestamp = kinesis_record.get("timestamp", None)
        player_country = kinesis_record.get("player_country", None)
        player_os = kinesis_record.get("player_os", None)
        player_level = kinesis_record.get("player_level", None)
        score = kinesis_record.get("score", None)
        # adding 1 day to expire ttl
        expiration = int(datetime.now().timestamp()) + 86400

        # check if some field is none
        if player_name is None or player_country is None or player_os is None or player_level is None:
            raise Exception(f"Mandatory fields can't be None") 

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
    except Exception as exc:
        # Handle schema validation error
        logger.error("Player data validation failed", error=str(exc))
        raise Exception(f"Player data validation failed {str(exc)}")


def lambda_handler(event, context):
    """
    Adding tracers to XRAY, using Powertools this can be done 
    via decorator and Powertools automatically creates segments and subsegments
    """
    segment = xray_recorder.begin_segment("initial")

    # Adding metrics to track the number of records to be processed at this time
    create_metrics_without_powertools("consumer_records_to_process", "Count", 1, "PowertoolsScoreboard")

    """
    We need to extract the event manually. If we use Powertools 
    we can use the data class to create an object from the event 
    and simply access its properties. 
    """
    subsegment = xray_recorder.begin_subsegment("processing_records")
    records = event.get("Records")

    for record in records:
        # adding annotation
        subsegment.put_annotation("record", record.get("eventID"))
        process_message(record)
        xray_recorder.end_subsegment()

    xray_recorder.end_subsegment()

    xray_recorder.end_segment()

def create_metrics_without_powertools(metric_name: str, unit: str, value: int, namespace: str):
    """ 
    This method uses the SDK, which incurs extra costs and network latency.
    Powertools uses CloudWatch EMF to serialize metrics
    """
    response = cloudwatch_client.put_metric_data(
        MetricData = [
            {
                'MetricName': metric_name,
                'Unit': unit,
                'Value': value
            },
        ],
        Namespace=namespace
    )

    return response