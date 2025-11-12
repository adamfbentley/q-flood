#!/bin/bash

# This script is designed to be run as a CustomAction OnNodeStart for AWS ParallelCluster.
# It installs Docker and Docker Compose, and configures the ec2-user to run Docker without sudo.

set -ex

log_file="/var/log/on_node_start.log"
exec > >(tee -a "$log_file") 2>&1

echo "Starting on_node_start.sh script..."

# Install Docker
yum update -y
yum install -y docker
service docker start
usermod -a -G docker ec2-user

echo "Docker installed and configured."

# Install Docker Compose
# Check for existing Docker Compose installation
if ! command -v docker-compose &> /dev/null
then
    echo "Installing Docker Compose..."
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d"v" -f2 | cut -d'"' -f1)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
    echo "Docker Compose ${DOCKER_COMPOSE_VERSION} installed."
else
    echo "Docker Compose is already installed."
fi

# Ensure Docker is running and ec2-user can use it
systemctl enable docker
systemctl start docker

# AWS-CQ-002: Note on group changes:
# The 'usermod -a -G docker ec2-user' command modifies the user's group membership.
# For this change to take effect, the user typically needs to log out and log back in,
# or explicitly run 'newgrp docker'. In an automated script context like CustomActions,
# the current shell session might not immediately reflect this change.
# Therefore, any subsequent Docker commands run by 'ec2-user' within the same script
# or immediately after might still require 'sudo' if the group change hasn't propagated.
# For robustness in automated scripts, consider explicitly using 'sudo docker-compose'
# or ensuring the commands are run by a user (e.g., root) that already has the necessary permissions.

echo "on_node_start.sh script finished."
