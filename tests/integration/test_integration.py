import json
import pytest
import requests
import boto3
from time import sleep

kinesis_client = boto3.client("kinesis") # type: ignore[attr-defined]
dynamodb_client = boto3.client("dynamodb") # type: ignore[attr-defined]

def test_api_gateway_score_endpoint(scorecard_api_endpoint):
    # GIVEN the scorecard API endpoint
    url = f"{scorecard_api_endpoint}?order=all"

    # WHEN we make a request
    response = requests.get(url)

    # THEN response must be 200
    assert response.status_code == 200

def test_summarized_data(scorecard_kinesis_stream, scorecard_summarized_table, fake_player):

    # GIVEN a message sent to Kinesis stream
    kinesis_client.put_record(
        StreamName=scorecard_kinesis_stream,
        Data=json.dumps(fake_player[0]),
        PartitionKey='shardId-000000000001',
    )

    # WHEN we query the data in DynamoDB looking for this specific player
    sleep(1)
    response = dynamodb_client.query(
        ExpressionAttributeValues={
            ':player_name': {
                'S': fake_player[0]["player_name"],
            },
        },
        KeyConditionExpression='player_name = :player_name',
        TableName=scorecard_summarized_table,
    )

    assert response["Count"] > 0
    # We can replace it with Powertools Event Source
    # I kept it using the pure DynamoDB response to be more explicit
    assert response["Items"][0]["player_name"]["S"] == fake_player[0]["player_name"]




