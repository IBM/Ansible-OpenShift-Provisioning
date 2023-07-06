xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python3
pip3 install ansible
ansible-galaxy collection install -r requirements.yaml
ansible-playbook playbooks/0_setup.yaml