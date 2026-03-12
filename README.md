# AWS S3 and EC2 Automation

Python scripts for AWS S3 static website deployment and EC2 instance management with robust exception handling.

## Project Overview

This project demonstrates practical AWS automation using Boto3, with a focus on writing resilient scripts that handle real-world errors including invalid credentials, region misconfigurations, and resource conflicts.

## What It Does

- Deploys static websites to S3 buckets with proper permissions
- Manages EC2 instances programmatically
- Handles exceptions for invalid credentials, duplicate bucket names, and region errors
- Accepts command line arguments for flexible script execution

## Technologies Used

- Python 3
- AWS S3
- AWS EC2
- Boto3 SDK
- AWS CLI

## Prerequisites

- Python 3 installed
- AWS CLI configured with valid credentials
- Required packages: `pip install -r requirements.txt`
