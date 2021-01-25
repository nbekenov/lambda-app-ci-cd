# CI/CD pipeline for Serverless application
## Building, testing, and deploying Serverless application using CodeBuild and CodePipeline


## Table of contents
* [General info](#general-info)
* [Solution](#solution)
* [Setup](#setup)
* [Cleanup](#contact)

## General info
This project includes the following files and folders.

## Solution
![Architecture diagram](./img/architecture.png)

1. Developer deploys the code into CodeCommit
2. CodePipeline start execution
3. CodeBuild outputs artifacts into S3 bucket
4. CodePipeline deploys CloudFormation stack in TEST account
5. Release manager reviews changes and approves/rejects in CodePipeline
6. If changes are approved CodePipeline deploys CloudFormation stack to the Production AWS account

## Setup:

### Pre-requisites
1. Install the AWS CLI.
2. Intall the SAM CLI.
3. Clone this repository.
4. Have the following AWS accounts: Test and Production

### 1. Create pipeline infrastructure
```
cd cloudformation
./create-pipeline.sh
```
### 2. Usage
TO DO

## Cleanup
```
cd cloudformation
./destroy.sh
```