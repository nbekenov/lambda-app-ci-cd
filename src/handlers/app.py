#!/usr/bin/env python3
"""
API code for displaying generic message or echoing a custom message
"""
import datetime
import json
import os
import logging
import botocore
import boto3

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

COUNTER_TABLE_NAME = os.getenv("TABLE_NAME","stellitime-api-counters")
COUNTER_KEY = os.getenv("COUNTER_KEY","demo-key")
region_name = os.getenv("REGION", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=region_name)
counter_table = dynamodb.Table(COUNTER_TABLE_NAME)

def lambda_handler(event, context):
    # pylint: disable=unused-argument
    """
    CLI interface to call GET and POST
    """
    logger.info(f"Received in get_from_dynamo: {json.dumps(event)}")
    operation = event['httpMethod']
    logger.info(f"Received from API operation: {operation}")

    if operation == "GET":  # pylint: disable=no-else-return
        return get()
    elif operation == "POST":
        if "body" in event:
            try:
                event = json.loads(event["body"])
            except:  # pylint: disable=bare-except
                logger.error("ERROR: malformed json input")
                return {"statusCode": 400, "body": "malformed json input"}
        body = event
        return post(body)
    else:
        logger.error("Received not get or post operation")
        return 1, """Usage: %s [ '{ "message" : "some-string" } ]""" % event


def get():
    """
    Returns generic message plus time
    """
    today = datetime.datetime.today()
    value = get_current_counter_item(COUNTER_KEY)
    timestamp = today.strftime("%m/%d/%Y:%H:%M:%S")
    data = {
            "counter_value": value,
            "message": "Automation For The People",
            "timestamp": timestamp
        }
    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }

def post(request_body):
    """
    Echos the message you sent in the body of the request in the response
    """
    value = increment_current_counter_item(COUNTER_KEY)
    today = datetime.datetime.today()

    if "message" not in request_body:
        return {"statusCode": 400, "body": "missing message in request body"}
    timestamp = today.strftime("%m/%d/%Y:%H:%M:%S")
    output_message = request_body["message"]
    data = {
            "counter_value": value,
            "message": output_message,
            "timestamp": timestamp
        }
    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }


def get_current_counter_item(key):
    """
    get counter_value of the item in DynamoDB
    """
    logger.info(f'getting id: {key} in table {COUNTER_TABLE_NAME}')
    try:
        get_item_response = counter_table.get_item(Key={"id": key})
        # create item if not found
        if "Item" not in get_item_response:
            item = create_new_counter_item(key, 1)
            get_item_response["Item"] = item
        return int(get_item_response["Item"]["counter_value"])
    except botocore.exceptions.ClientError as error:
        logger.error("get_item failed", exc_info=True)
        raise error from error


def increment_current_counter_item(key):
    """
    increment item in DynamoDB
    """
    logger.info(f'updating id: {key} in table {COUNTER_TABLE_NAME}')
    update_item_response = counter_table.update_item(
        TableName=COUNTER_TABLE_NAME,
        Key={"id": key},
        ExpressionAttributeNames={"#field": "counter_value"},
        ExpressionAttributeValues={":increment": 1},
        UpdateExpression="ADD #field :increment",
        ReturnValues="UPDATED_NEW",
    )
    return int(update_item_response["Attributes"]["counter_value"])


def create_new_counter_item(key, value):
    """
    create new item in DynamoDB
    """
    item = {"id": key, "counter_value": value}
    logger.info(f'creating new item with id: {key} and counter_value: {value}')
    try:
        put_item_response = counter_table.put_item(Item=item)
        logger.info(f'put_item_response: {put_item_response}')
        return item
    except botocore.exceptions.ClientError as error:
        logger.error("put_item failed", exc_info=True)
        raise error from error
