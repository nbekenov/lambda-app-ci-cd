#!/usr/bin/env bash
echo -n "Enter Test Account > "
read TestAccount
echo -n "Enter TestAccount ProfileName for AWS Cli operations> "
read TestAccountProfile
echo -n "Enter Prod Account > "
read ProdAccount
echo -n "Enter ProdAccount ProfileName for AWS Cli operations> "
read ProdAccountProfile

echo -n "Deploying pre-requisite stack to the tools account... "
aws cloudformation deploy --stack-name pre-reqs --template-file pre-reqs.yaml --parameter-overrides TestAccount=$TestAccount ProductionAccount=$ProdAccount --profile $TestAccountProfile
echo -n "Fetching S3 bucket and CMK ARN from CloudFormation automatically..."
get_s3_command="aws cloudformation describe-stacks --stack-name pre-reqs --profile $TestAccountProfile --query \"Stacks[0].Outputs[?OutputKey=='ArtifactBucket'].OutputValue\" --output text"
S3Bucket=$(eval $get_s3_command)
echo -n "Got S3 bucket name: $S3Bucket"

get_cmk_command="aws cloudformation describe-stacks --stack-name pre-reqs --profile $TestAccountProfile --query \"Stacks[0].Outputs[?OutputKey=='CMK'].OutputValue\" --output text"
CMKArn=$(eval $get_cmk_command)
echo -n "Got CMK ARN: $CMKArn"

echo -n "Executing in TEST Account"
aws cloudformation deploy --stack-name toolsacct-codepipeline-role --template-file codecommit-role.yaml --capabilities CAPABILITY_NAMED_IAM --parameter-overrides TestAccount=$TestAccount CMKARN=$CMKArn --profile $TestAccountProfile

echo -n "Executing in TEST Account"
aws cloudformation deploy --stack-name toolsacct-codepipeline-cloudformation-role --template-file cloudformation-deployer-role.yaml --capabilities CAPABILITY_NAMED_IAM --parameter-overrides TestAccount=$TestAccount CMKARN=$CMKArn  S3Bucket=$S3Bucket --profile $TestAccountProfile

echo -n "Executing in PROD Account"
aws cloudformation deploy --stack-name toolsacct-codepipeline-cloudformation-role --template-file cloudformation-deployer-role.yaml --capabilities CAPABILITY_NAMED_IAM --parameter-overrides TestAccount=$TestAccount CMKARN=$CMKArn  S3Bucket=$S3Bucket --profile $ProdAccountProfile

echo -n "Creating Pipeline in TEST Account"
aws cloudformation deploy --stack-name sample-lambda-pipeline --template-file code-pipeline.yaml --parameter-overrides TestAccount=$TestAccount ProductionAccount=$ProdAccount CMKARN=$CMKArn S3Bucket=$S3Bucket --capabilities CAPABILITY_NAMED_IAM --profile $TestAccountProfile

echo -n "Adding Permissions to the CMK"
aws cloudformation deploy --stack-name pre-reqs --template-file pre-reqs.yaml --parameter-overrides CodeBuildCondition=true --profile $TestAccountProfile

echo -n "Adding Permissions to the Cross Accounts"
aws cloudformation deploy --stack-name sample-lambda-pipeline --template-file code-pipeline.yaml --parameter-overrides CrossAccountCondition=true --capabilities CAPABILITY_NAMED_IAM --profile $TestAccountProfile