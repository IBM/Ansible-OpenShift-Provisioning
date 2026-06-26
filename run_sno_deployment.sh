#!/bin/bash
# SNO Deployment Script
# This script sets the required environment variables and runs the master playbook

# Set the inventory directory
export ANSIBLE_INVENTORY_DIR="inventories/default"

# Run the master playbook for ABI
ansible-playbook playbooks/master_playbook_for_abi.yaml -e "inventory_dir=${PWD}/inventories/default"

echo ""
echo "Deployment initiated. Monitor the installation progress on the bastion host."

# Made with Bob
