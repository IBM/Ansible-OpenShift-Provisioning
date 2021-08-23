#!/bin/bash

ansible-galaxy collection install community.general
ansible-galaxy collection install community.crypto
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.libvirt
sudo dnf install sshpass -y
sudo dnf install openssh -y
sudo dnf install ssh-copy-id -y