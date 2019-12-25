from sshtunnel import SSHTunnelForwarder

# This python file's only purpose of this code is to SSH tunnel into the deployment server from a development environment.
# This code will not be used by the deployment server.

db_port = 3306
remote_user = "ubuntu"
remote_key = "./credentials/648team13.pem"
remote_host = "ec2-3-17-190-122.us-east-2.compute.amazonaws.com"
remote_port = 22
localhost = "127.0.0.1"

server = SSHTunnelForwarder(
    ssh_address_or_host=(remote_host, remote_port),
    ssh_username=remote_user,
    ssh_pkey=remote_key,
    remote_bind_address=(localhost, db_port),
)