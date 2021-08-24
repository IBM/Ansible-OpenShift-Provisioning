#!/bin/bash

ansible-galaxy collection install community.general
ansible-galaxy collection install community.crypto
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.libvirt
brew install sshpass -y
brew install openssh -y