Terraform AWS EC2 and Load Balancer Deployment
This project uses Python and Terraform to deploy an EC2 instance and an Application Load Balancer (ALB) on AWS. It also verifies the deployment using boto3.

Prerequisites
* AWS CLI configured with your credential
* Python 3 installed
* Terraform installed
* Required Python packages: jinja2, python-terraform, boto3

You can install Python packages using:
pip install jinja2 python-terraform boto3
How to Use
Run the Python script to create the Terraform configuration and deploy 

resources:
python3 py_create_ec2.py
Follow the prompts:

Choose AMI: ubuntu or amazon_linux

Choose instance type: t3.small or t3.medium

Enter the Load Balancer name

The script will:

Generate a Terraform file

Initialize Terraform

Plan and apply the deployment

Verify the deployed resources using AWS SDK (boto3)

Save verification results to aws_validation.json

Terraform Template
The Terraform template uses variables such as:

region: AWS region (fixed to us-east-2)

availability_zone: fixed to us-east-2a

ami: AMI ID based on user choice

instance_type: EC2 instance size

load_balancer_name: user provided

Verification
After deployment, the script verifies:

The EC2 instance is running

Retrieves the instance's public IP

Checks that the ALB exists and fetches its DNS name

Verification data is saved in aws_validation.json.

Screenshot
Add your screenshot here:


Cleanup
To destroy the created AWS resources, run:

bash
Copy
Edit
terraform destroy
Troubleshooting
Make sure your AWS credentials are set correctly.

Check that the required subnets and VPC IDs in the Terraform template match your AWS environment.

If Terraform commands fail, review the error messages printed by the script.

