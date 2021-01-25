import json
import boto3
import os
import logging

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    logger.info("Entering PreTraffic Hook!")
    #Read the DeploymentId and LifecycleEventHookExecutionId from the event payload
    deploymentId = event["DeploymentId"]
    lifecycleEventHookExecutionId = event["LifecycleEventHookExecutionId"]
    functionToTest = os.environ["NewVersion"]
    
    logger.info("BeforeAllowTraffic hook tests started")
    logger.info("Testing new function version: " + functionToTest)

    #Create parameters to pass to the updated Lambda function
    payload = {
        "body": '{ "test": "body"}',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "GET",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "GET",
        "stageVariables": {"baz": "qux"},
        "path": "/examplepath",
    }
    
    status = "Failed"
    #Invoke the updated Lambda function.
    lambda_client = boto3.client("lambda")
    try:
        resp = lambda_client.invoke(
            FunctionName=functionToTest,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        result = json.loads(resp["Payload"].read().decode("utf-8"))
        #Check if the status code returned by the updated function
        if result["statusCode"] == 200:
            status = "Succeeded"
            logger.info("Validation succeeded")
        else:
            status = "Failed"
            logger.info("Validation failed")
    except Exception as error:
        logger.info(error)
        status = "Failed"
    
    #Pass AWS CodeDeploy the prepared validation test results.
    try:
        codedeploy_client = boto3.client("codedeploy")
        _ = codedeploy_client.put_lifecycle_event_hook_execution_status(
            deploymentId=deploymentId,
            lifecycleEventHookExecutionId=lifecycleEventHookExecutionId,
            status=status,
        )
        logger.info("CodeDeploy status updated successfully")
    except Exception as error:
        logger.info("CodeDeploy Status update failed")
        logger.info(error)