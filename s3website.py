import boto3
import json
import pprint
from botocore.exceptions import ClientError
import argparse
import random

def generate_random_string(length=10):
    #Generate a random string of lowercase letters and digits for unique bucket names
    letters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(letters) for i in range(length))

def bucket_name_available(bucket_name):
    #Check if a bucket name is available to create.
    #Returns True if bucket doesn't exist and False otherwise.
    
    answer = False
    client = boto3.client("s3")
    
    try:
        response = client.head_bucket(Bucket=bucket_name)
        pprint.pprint(response)
        print(f"Bucket {bucket_name} exists and you own it.")
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print(f"Bucket {bucket_name} does not exist.")
            answer = True
        elif error_code == 403:
            print(f"Bucket {bucket_name} exists but you do not have access to it.")
        else:
            print(f"Error checking bucket {bucket_name}: {e}")
    
    return answer


def create_bucket(bucket_name):
    #Create an S3 bucket in my default region
    client = boto3.client("s3")
    response = client.create_bucket(Bucket=bucket_name)
    print(f"Bucket {bucket_name} created.")


def put_bucket_website(bucket_name):
    #Configure the S3 bucket for static website hosting
    client = boto3.client("s3")
    response = client.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html',
            },
            'IndexDocument': {
                'Suffix': 'index.html',
            },
        },
    )
    print(f"Bucket {bucket_name} configured for website hosting.")


def upload_files(bucket_name):
    #Uploads index.html and error.html files to the S3 bucket
    client = boto3.client("s3")
    
    indexFile = open("index.html", "rb")
    client.put_object(
        Body=indexFile,
        Bucket=bucket_name,
        Key="index.html",
        ContentType="text/html"
    )
    indexFile.close()

    errorFile = open("error.html", "rb")
    client.put_object(
        Body=errorFile,
        Bucket=bucket_name,
        Key="error.html",
        ContentType="text/html"
    )
    errorFile.close()
    print("Uploaded index.html and error.html to bucket.")


def remove_public_access_block(bucket_name):
    #Remove the public access block to allow public access to the bucket
    client = boto3.client("s3")
    client.delete_public_access_block(Bucket=bucket_name)
    print(f"Removed public access block from bucket {bucket_name}.")


def set_bucket_policy(bucket_name):
    #Set bucket policy to allow public read access to all objects
    client = boto3.client("s3")
    
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Statement1",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::%s/*" % bucket_name
            }
        ]
    }

    bucket_policy_string = json.dumps(bucket_policy)
    client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy_string)
    print(f"Bucket policy applied to bucket {bucket_name}.")
    print(f"Bucket {bucket_name} is now publicly accessible and configured for static website hosting.")


def remove_bucket(bucket_name):
    #Delete an S3 bucket (must be empty)
    client = boto3.client("s3")
    try:
        response = client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} deleted.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketNotEmpty':
            print(f"Bucket {bucket_name} is not empty. Please remove all files before deleting.")
        else:
            print(f"Error deleting bucket {bucket_name}: {e}") 


def remove_all_objects(bucket_name):
    #Remove all objects from an S3 bucket
    client = boto3.client("s3")
    try:
        response = client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            for item in response['Contents']:
                print(f"Deleting {item['Key']} from {bucket_name}")
                client.delete_object(Bucket=bucket_name, Key=item['Key'])
        else:
            print(f"No objects found in bucket {bucket_name}.")
    except ClientError as e:
        print(f"Error removing objects from bucket {bucket_name}: {e}")


def remove_all_buckets():
    """Remove all buckets in the account (use with caution!)"""
    client = boto3.client("s3")
    try:
        response = client.list_buckets()
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            print(f"Processing bucket: {bucket_name}")
            remove_all_objects(bucket_name)
            remove_bucket(bucket_name)
    except ClientError as e:
        print(f"Error listing buckets: {e}")


def main():
    parser = argparse.ArgumentParser(description="Create and configure an S3 bucket for static website hosting.")
    parser.add_argument("--sitename", type=str, help="The name of the S3 bucket to create.")
    args = parser.parse_args()
    
    if args.sitename:
        bucket_name = args.sitename
    else:
        random_suffix = generate_random_string()
        bucket_name = f"my-website-{random_suffix}"
    
    print(f"Using bucket name: {bucket_name}")
    
    client = boto3.client("s3")
    
    try:
        create_bucket(bucket_name)
        put_bucket_website(bucket_name)
        upload_files(bucket_name)
        remove_public_access_block(bucket_name)
        set_bucket_policy(bucket_name)
        
    except client.exceptions.BucketAlreadyExists as err:
        print("Bucket {} already exists!".format(err.response['Error']['BucketName']))
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Error Code: {error_code}")
        
        if error_code == 'InvalidClientTokenId' or error_code == 'SignatureDoesNotMatch'or error_code == 'InvalidToken':
            print("Please update your ~/.aws/credentials file with valid credentials.")


if __name__ == "__main__":
    main()