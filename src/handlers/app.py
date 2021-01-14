#!/usr/bin/env python3
"""
API code for displaying generic message or echoing a custom message v3
"""
import boto3
import datetime
import json
import os
import logging

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
    CLI interface to call GET and POST for
    """
    logger.info(f'Input event : {event}')
    operation = event["requestContext"]["http"]["method"]
    logger.info("Received from API operation: " + operation)

    if operation == "GET":  # pylint: disable=no-else-return
        return 0, get()
    elif operation == "POST":
        if "body" in event:
            try:
                event = json.loads(event["body"])
            except:  # pylint: disable=bare-except
                logger.error("ERROR: malformed json input")
                return 1, {"statusCode": 400, "body": "malformed json input"}
        body = event
        return 0, post(body)
    else:
        logger.error("Received not get or post operation")
        return 1, """Usage: %s [ '{ "message" : "some-string" } ]""" % event


def get():
    """
    Returns generic message plus time
    """
    today = datetime.datetime.today()
    value = get_current_counter_item(COUNTER_KEY, counter_table)
    return {
        "statusCode": 200,
        "body": {
            "counter_value": value,
            "message": "Automation For The People",
            "timestamp": today.strftime("%m/%d/%Y:%H:%M:%S"),
        },
    }


def post(request_body):
    """
    Echos the message you sent in the body of the request in the response
    """
    value = increment_current_counter_item(COUNTER_KEY, counter_table)
    today = datetime.datetime.today()

    if "message" not in request_body:
        return {"statusCode": 400, "body": "missing message in request body"}
    return {
        "statusCode": 200,
        "body": {
            "counter_value": value,
            "message": request_body["message"],
            "timestamp": today.strftime("%m/%d/%Y:%H:%M:%S"),
        },
    }


def get_current_counter_item(key, table):
    logger.info(f'getting id: {key}')
    try:
        get_item_response = table.get_item(Key={"id": key})
        # create item if not found
        if "Item" not in get_item_response:
            item = create_new_counter_item(key, 1)
            get_item_response["Item"] = item
        return int(get_item_response["Item"]["counter_value"])
    except Exception as e:
        logger.error("get_item failed")
        logger.error(e)
        raise SystemExit(e)


def increment_current_counter_item(key, table):
    update_item_response = table.update_item(
        TableName=COUNTER_TABLE_NAME,
        Key={"id": key},
        ExpressionAttributeNames={"#field": "counter_value"},
        ExpressionAttributeValues={":increment": 1},
        UpdateExpression="ADD #field :increment",
        ReturnValues="UPDATED_NEW",
    )
    return int(update_item_response["Attributes"]["counter_value"])


def create_new_counter_item(key, value):
    item = {"id": key, "counter_value": value}
    put_item_response = counter_table.put_item(Item=item)
    return put_item_response
