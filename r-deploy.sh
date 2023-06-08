#!/bin/bash
ENVIRONMENT=dev
AWS_REGION=sa-east-1

KEYPAIR="RingerKey"
AVAILABLE_KEY=`aws ec2 describe-key-pairs --key-name $KEYPAIR --region sa-east-1 | grep KeyName | awk -F\" '{print $4}'`

if [ "$KEYPAIR" = "$AVAILABLE_KEY" ]; then
    echo "Key is available."
else
    echo "Key is not available: Creating new key"
    aws ec2 create-key-pair --key-name $KEYPAIR --region $AWS_REGION | python -c "import json,sys;obj=json.load(sys.stdin);secret = obj['KeyMaterial'];f=open('RingerKey.pem', 'w');f.write(secret);f.close()"
    aws secretsmanager create-secret --name EC2Keypair --region $AWS_REGION --secret-string "$(< RingerKey.pem)"
    rm RingerKey.pem
fi


sam deploy --template-file resources.yml --s3-bucket ringer-$ENVIRONMENT-init --s3-prefix ringer-init/stack-ringer-init --region $AWS_REGION --stack-name stack-ringer-init --parameter-overrides ParameterKey=ENV,ParameterValue=$ENVIRONMENT ParameterKey=KeyPairName,ParameterValue=$KEYPAIR --no-fail-on-empty-changeset --capabilities CAPABILITY_NAMED_IAM