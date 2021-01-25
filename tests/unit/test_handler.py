import boto3
import json
import pytest
import os
from unittest import mock
from random import randrange

COUNTER_KEY = os.getenv("COUNTER_KEY", "demo-key")

@mock.patch.dict(os.environ, {"TABLE_NAME": 'test-dynamodb-table'})
def test_get(apigw_get_event, dynamodb_table):
    from src.handlers import app
    table = boto3.resource("dynamodb", region_name="us-east-1").Table('test-dynamodb-table')
    random_item_number = randrange(3,100)
    item = {"id": COUNTER_KEY, "counter_value": random_item_number}
    table.put_item(Item=item)
    ret = app.lambda_handler(apigw_get_event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert data["counter_value"] == random_item_number

@mock.patch.dict(os.environ, {"TABLE_NAME": 'test-dynamodb-table'})
def test_post(apigw_post_event, dynamodb_table):
    from src.handlers import app
    ret = app.lambda_handler(apigw_post_event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert data["counter_value"] == 1
    assert data["message"] == "unit-test"