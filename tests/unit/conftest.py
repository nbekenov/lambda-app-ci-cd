# conftest.py
import os
import boto3
import pytest
from moto import mock_dynamodb2

table_name = os.getenv("TBALE_NAME", "stellitime-api-counters")
COUNTER_KEY = os.getenv("COUNTER_KEY", "demo-key")
region_name = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture(scope="function")
def dynamodb_table():
    """Create a DynamoDB table fixture."""

    @mock_dynamodb2
    def dynamodb_client():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        counter_table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        counter_table = dynamodb.Table(table_name)
        item = {"id": COUNTER_KEY, "counter_value": 29}
        counter_table.put_item(Item=item)
        return counter_table

    return dynamodb_client