from typing import List

import boto3


def build_and_query_dynamodb(dynamodb_client, order_by: str, filter: str = "") -> str:
    scan_params = {"TableName": "ScoreboardSummedUpData"}

    if order_by == "player_country":
        scan_params["FilterExpression"] = "player_country = :player_country"
        scan_params["ExpressionAttributeValues"] = {":player_country": {"S": filter}}

    if order_by == "player_level":
        scan_params["FilterExpression"] = "player_level = :player_level"
        scan_params["ExpressionAttributeValues"] = {":player_level": {"S": filter}}

    response = dynamodb_client.scan(**scan_params)

    items = response["Items"]
    sorted_items = sorted(items, key=lambda x: int(x["score"]["N"]), reverse=True)

    return sorted_items


class DynamoDBBatchHelper:
    """
    Helper class for performing batch write operations in DynamoDB.
    """

    BATCH_SIZE = 25

    def __init__(self, boto3_client: boto3.client, table_name: str) -> None:
        """
        Initializes the DynamoDBBatchHelper instance.

        Args:
            boto3_client (boto3.client): The Boto3 client for DynamoDB.
            table_name (str): The name of the DynamoDB table.
        """
        self._boto3_client: boto3.client = boto3_client
        self._items: List[dict] = []
        self.table_name = table_name

    def __del__(self):
        self._flush_to_dynamodb()

    def put_item(self, item: dict):
        """
        Adds an item to the batch.

        Args:
            item (dict): The item to be added to the batch.
        """
        self._items.append(item)

        # Flush to DynamoDB when reaching batch size
        if len(self._items) == self.BATCH_SIZE:
            self._flush_to_dynamodb()

    def _flush_to_dynamodb(self):
        """
        Flushes the batched items to DynamoDB using batch write operation.
        The limit is 25 per batch operation
        """
        # Prepare the batch write item request
        print(self._items)
        request_items = {
            self.table_name: [{"PutRequest": {"Item": item}} for item in self._items]
        }

        # Perform the batch write operation
        response = self._boto3_client.batch_write_item(RequestItems=request_items)

        # Check for any unprocessed items
        unprocessed_items = response.get("UnprocessedItems", {})
        while unprocessed_items:
            response = self._boto3_client.batch_write_item(
                RequestItems=unprocessed_items
            )
            unprocessed_items = response.get("UnprocessedItems", {})

        ## TODO: Add error handling

        # Reset the items
        self._items = []
