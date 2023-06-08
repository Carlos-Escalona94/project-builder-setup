import subprocess

from pygit2 import Repository
import boto3
from botocore.client import ClientError

project_name = "project-builder"
allowed_branches = ["master"]

setup_bucket_name = f"{project_name}-setup"

aws_project_account = "897757051609"
aws_default_region = "sa-east-1"
# #There are best places for this
# AWS_PROJECT_ACCOUNT="630559342914"

# SESSION_ACCOUNT=`aws sts get-caller-identity --region $AWS_REGION | grep Account | awk -F\" '{print $4}'`

sts_client = boto3.client('sts')
s3_client = boto3.resource('s3', region_name = aws_default_region)

def main():
    git_branch = Repository('.').head.shorthand

    if(not git_branch in allowed_branches):
        raise
    
    account_id = sts_client.get_caller_identity().get('Account')

    if(not account_id == aws_project_account):
        raise

    try:
        s3_client.meta.client.head_bucket(Bucket=setup_bucket_name)
    except ClientError:
        print("Bucket not exits - creating")
        s3_client.create_bucket(Bucket=setup_bucket_name, CreateBucketConfiguration={'LocationConstraint': aws_default_region})
    # The bucket does not exist or you have no access.


    result = subprocess.call(['sam.cmd', 'deploy', '--template-file', './resources.yml', '--capabilities', 'CAPABILITY_NAMED_IAM', '--s3-bucket', setup_bucket_name, '--s3-prefix', 'project/stack-setup', '--region', aws_default_region, '--stack-name', 'stack-setup', '--parameter-overrides', f'ProjectName={project_name}', f'DefaultRegion={aws_default_region}', '--no-fail-on-empty-changeset'])

    print(result)

    


if __name__ == "__main__":
    main()