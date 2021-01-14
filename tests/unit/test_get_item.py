import boto3
import pytest
import os
from src.handlers.app import *
from moto import mock_dynamodb2

COUNTER_KEY = os.getenv("COUNTER_KEY", "demo-key")
table_name = os.getenv("TBALE_NAME", "stellitime-api-counters")


@mock_dynamodb2
def test_get_current_counter_item(dynamodb_table):
    dynamodb_table()
    table = boto3.resource("dynamodb", region_name="us-east-1").Table(table_name)
    get_item_response = get_current_counter_item(COUNTER_KEY, table)
    assert get_item_response == 29


@mock_dynamodb2
def test_inc_item_response(dynamodb_table):
    dynamodb_table()
    table = boto3.resource("dynamodb", region_name="us-east-1").Table(table_name)
    inc_item_response = increment_current_counter_item(COUNTER_KEY, table)
    assert inc_item_response == 29 + 1