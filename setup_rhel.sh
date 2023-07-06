sudo dnf install python3 -y
pip3 install ansible
ansible-galaxy collection install -r requirements.yaml
ansible-playbook playbooks/0_setup.yaml