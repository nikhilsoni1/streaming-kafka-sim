import click
from aws_repository.services.ec2_service import start_ec2_instance, stop_ec2_instance, update_instance_ip

@click.group()
def ec2():
    """EC2 related operations"""

@ec2.command()
@click.option('--instance-id', required=True, help='ID of the EC2 instance to stop')
def stop_instance(instance_id):
    stop_ec2_instance(instance_id)

@ec2.command()
@click.option('--instance-id', required=True, help='ID of the EC2 instance to start')
def start_instance(instance_id):
    start_ec2_instance(instance_id)

@ec2.command()
@click.option('--instance-id', required=True, help='ID of the EC2 instance to update')
@click.option('--new-ip', required=True, help='New public IP address')
def update_ip(instance_id, new_ip):
    update_instance_ip(instance_id, new_ip)