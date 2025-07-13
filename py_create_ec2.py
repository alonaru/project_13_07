from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from python_terraform import Terraform
import os

# Fixed AWS region
region = "us-east-2"

try:
    # Ask user for input
    ami_choice = input("Choose AMI (ubuntu or amazon_linux): ").strip().lower()
    if ami_choice == "ubuntu":
        ami = "ami-0c995fbcf99222492"  # Replace with actual Ubuntu AMI
    elif ami_choice == "amazon_linux":
        ami = "ami-0915e09cc7ceee3ab"  # Replace with actual Amazon Linux AMI
    else:
        print("Invalid AMI choice. Defaulting to Ubuntu.")
        ami = "ami-0c995fbcf99222492"

    instance_type = input("Choose instance type (t3.small or t3.medium): ").strip()
    if instance_type not in ["t3.small", "t3.medium"]:
        print("Invalid input. Defaulting to t3.small.")
        instance_type = "t3.small"

    az = input("Enter availability zone (e.g., us-east-2a): ").strip()
    if not az.startswith(region):
        az = region + "a"
        print("Invalid AZ. Defaulting to", az)

    lb_name = input("Enter Load Balancer name: ").strip()
    if not lb_name:
        raise ValueError("Load balancer name cannot be empty.")

    # Prepare template variables
    variables = {
        "ami": ami,
        "instance_type": instance_type,
        "availability_zone": az,
        "load_balancer_name": lb_name,
        "region": region
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

    # Run Terraform
    tf = Terraform()
    print("Running terraform init...")
    return_code, stdout, stderr = tf.init()
    if return_code != 0:
        raise RuntimeError("Terraform init failed:\n" + stderr)

    print("Running terraform apply...")
    return_code, stdout, stderr = tf.apply(skip_plan=True)
    if return_code != 0:
        raise RuntimeError("Terraform apply failed:\n" + stderr)

    print("Done! Resources should be deployed.")
    
except ValueError as ve:
    print("Input error:", ve)

except RuntimeError as re:
    print("Terraform error:", re)

except Exception as e:
    print("Unexpected error:", e)
