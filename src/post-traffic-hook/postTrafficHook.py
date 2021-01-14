import json
import boto3
import os
import logging

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    logger.info("Entering PostTraffic Hook!")
    #Read the DeploymentId and LifecycleEventHookExecutionId from the event payload
    deploymentId = event["DeploymentId"]
    lifecycleEventHookExecutionId = event["LifecycleEventHookExecutionId"]
    functionToTest = os.environ["NewVersion"]
    
    logger.info("AfterAllowTraffic hook tests started")
    logger.info("Testing new function version: " + functionToTest)

    #Create parameters to pass to the updated Lambda function
    payload = {"requestContext": {"http": {"method": "GET"}}}
    
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
        if result[1]["statusCode"] == 200:
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