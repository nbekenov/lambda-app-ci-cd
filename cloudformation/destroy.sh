#!/usr/bin/env bash
echo -n "You are going to destory pipeline and all related configuration. Are you sure? > "
read answer

echo -n "Enter Test Account > "
read TestAccount
echo -n "Enter TestAccount ProfileName for AWS Cli operations> "
read TestAccountProfile
echo -n "Enter Prod Account > "
read ProdAccount
echo -n "Enter ProdAccount ProfileName for AWS Cli operations> "
read ProdAccountProfile

echo "====================="
aws cloudformation delete-stack --stack-name toolsacct-codepipeline-cloudformation-role --profile $ProdAccountProfile
echo "====================="
aws cloudformation delete-stack --stack-name sample-lambda-pipeline --profile $TestAccountProfile
echo "====================="
aws cloudformation delete-stack --stack-name toolsacct-codepipeline-cloudformation-role --profile $TestAccountProfile
echo "====================="
aws cloudformation delete-stack --stack-name pre-reqs --profile $TestAccountProfile
echo "====================="
aws cloudformation delete-stack --stack-name toolsacct-codepipeline-role --profile $TestAccountProfile