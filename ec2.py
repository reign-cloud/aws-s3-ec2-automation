import boto3
import pprint
from botocore.exceptions import ClientError

DRYRUN = False

def main():
    client = boto3.client('ec2')

    try:
        ami = Get_ImageId(client)
        instance_id = Create_EC2_instance(ami, client)

        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(instance_id)

        print(f"Instance ID: {instance.instance_id}")
        print(f"Instance State (before waiting): {instance.state['Name']}")
        instance.wait_until_running()
        instance.reload()
        print(f"Instance State (after waiting): {instance.state['Name']}")
        print(f"Public IP Address: {instance.public_ip_address}")
        print(f"Current Tags:")
        if instance.tags:
            for tag in instance.tags:
                print(f"  {tag['Key']}: {tag['Value']}")
        else:
                print(" No tags found")
        instance.create_tags(
                Tags=[
                {
                        'Key': 'Name',
                        'Value': 'Rane'
                }              
                ]
        )
        instance.reload()
        print("Updated Tags:")
        if instance.tags:
                for tag in instance.tags:
                    print(f" {tag['Key']}: {tag['Value']}")
        else:
                print("  No tags found")

        print(f"Instance State (before termination): {instance.state['Name']}")
        instance.terminate()
        instance.wait_until_terminated()
        instance.reload()
        print(f"Instance State (after termination): {instance.state['Name']}")
    
    except ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == 'UnauthorizedOperation':
             print("Please check your region configuration in your .aws config file")

def Get_ImageId(client):
    images_response = client.describe_images(
        Filters=[
            {
                'Name': 'description',
                'Values': ["Amazon Linux 2 AMI*"]
            },
            {
                'Name' : 'architecture',
                'Values': ['x86_64']
            },
            {
                'Name': 'owner-alias',
                'Values': ['amazon']
            }
        ]
    )

    image_id = images_response["Images"][0]["ImageId"]
    return image_id

def Create_EC2_instance(ami, client):
    instance_response = client.run_instances(
        ImageId=ami,
        InstanceType="t2.micro",
        MaxCount=1,
        MinCount=1,
        DryRun=DRYRUN,
        SecurityGroups=['WebSG'],
        KeyName='vockey',
        UserData='''
            #!/bin/bash ex
            # Updated to use Amazon Linux 2
            yum -y update
            yum -y install httpd php mysql php-mysql wget unzip
            /usr/bin/systemctl enable httpd
            /usr/bin/systemctl start httpd
            cd /var/www/html
            wget https://aws-tc-largeobjects.s3-us-west-2.amazonaws.com/CUR-TF-100-ACCLFO-2/lab6-scaling/lab-app.zip
            unzip lab-app.zip -d /var/www/html/
            chown apache:root /var/www/html/rds.conf.php
        '''
    )
    instance_id =instance_response["Instances"][0]["InstanceId"]
    return instance_id

if __name__ == "__main__":
    main()