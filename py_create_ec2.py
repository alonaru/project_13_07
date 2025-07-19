import traceback
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from python_terraform import Terraform
import boto3
import json

try:
    # Ask user for region and AZs
    region = input("Enter AWS region (e.g., eu-west-1): ").strip()
    az1 = region + "a"
    az2 = region + "b"


    # Ask user for input
    ami_choice = input("Choose AMI (ubuntu or amazon_linux): ").strip().lower()
    if ami_choice == "ubuntu":
        ami = "ami-01f23391a59163da9"  # Replace with actual Ubuntu AMI
    elif ami_choice == "amazon_linux":
        ami = "ami-0b3e7dd7b2a99b08d"  # Replace with actual Amazon Linux AMI
    else:
        print("Invalid AMI choice. Defaulting to Ubuntu.")
        ami = "ami-01f23391a59163da9"

    instance_type = input("Choose instance type (t3.small or t3.medium): ").strip()
    if instance_type not in ["t3.small", "t3.medium"]:
        print("Invalid input. Defaulting to t3.small.")
        instance_type = "t3.small"

    lb_name = input("Enter Load Balancer name: ").strip()
    if not lb_name:
        raise ValueError("Load balancer name cannot be empty.")

    # Prepare template variables
    variables = {
        "ami": ami,
        "instance_type": instance_type,
        "region": region,
        "az1": az1,
        "az2": az2,
        "load_balancer_name": lb_name
    }

    # Load and render the template
    env = Environment(loader=FileSystemLoader("."))
    try:
        template = env.get_template("main.tf.j2")
    except TemplateNotFound:
        print("Error: Could not find 'main.tf.j2'. Make sure it exists in the current directory.")
        exit(1)

    rendered_tf = template.render(variables)

    # Write rendered template to main.tf
    with open("main.tf", "w") as f:
        f.write(rendered_tf)
    print("Terraform file created as main.tf")

    # Initialize Terraform
    tf = Terraform()
    print("Running terraform init...")
    return_code, stdout, stderr = tf.init()
    if return_code != 0:
        raise RuntimeError(f"Terraform init failed:\n{stderr}")

    # Run terraform plan
    print("Running terraform plan...")
    ret_code, out, err = tf.plan()
    print(out)  # Show terraform plan output
    print(err)  # Show terraform plan errors

    # Accept return codes 0 (no changes) or 2 (changes planned)
    if ret_code not in [0, 2]:
        raise RuntimeError(f"Terraform plan failed:\n{err}")

    # Run terraform apply (auto approve) with real-time output
    print("Running terraform apply...")
    ret_code, out, err = tf.apply(capture_output=False)
    # Output is shown in real time, but still check return code
    if ret_code not in [0, 2]:
        raise RuntimeError(f"Terraform apply failed. See above for details.")

    print("Done! Resources should be deployed.")
    



    # Get Terraform outputs
    outputs = tf.output(json=True)
    print("Raw tf.output result:", outputs)
    instance_id = outputs['instance_id']['value']
    alb_dns_name = outputs['alb_dns_name']['value']

    # Create boto3 clients
    ec2 = boto3.client('ec2', region_name=region)
    elb = boto3.client('elbv2', region_name=region)

    # Describe EC2 instance
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    instance_state = instance['State']['Name']
    public_ip = instance.get('PublicIpAddress', 'N/A')

    # Check ALB existence
    lbs = elb.describe_load_balancers()['LoadBalancers']
    alb_exists = any(lb['DNSName'] == alb_dns_name for lb in lbs)
    if not alb_exists:
        print(f"Warning: ALB with DNS {alb_dns_name} not found!")

    # Save to JSON file
    validation_data = {
        "instance_id": instance_id,
        "instance_state": instance_state,
        "public_ip": public_ip,
        "load_balancer_dns": alb_dns_name
    }

    with open("aws_validation.json", "w") as f:
        json.dump(validation_data, f, indent=4)

    print("Validation complete. Data saved to aws_validation.json")
    print(validation_data)
    # --- AWS Validation ends here ---


except ValueError as ve:
    print("Input error:", ve)

except RuntimeError as re:
    print("Terraform error:", re)

# ...existing code...
except Exception as e:
    print("Unexpected error:", e)
    traceback.print_exc()
