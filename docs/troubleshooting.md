# Troubleshooting
If you encounter errors while running the main playbook, there are a few things you can do:  

* Double check your variables.  
* Inspect the part that failed by opening the playbook or role at roles/role-name/tasks/main.yaml  
* Google the specific error message.  
* Re-run the role indivually with [tags](vault-and-tags.md) or with the verbosity '-v' option to get more debugging information (more v's give more info). For example:  
```
ansible-playbook main.yaml --tags get_ocp -vvv --ask-vault-pass
```
* Teardown the KVM host with the delete_partition.yaml playbook or teardown troublesome KVM guests with the [teardown](teardown.md) playbooks.
* E-mail Jacob Emery at jacob.emery@ibm.com
* If it's a problem with an OpenShift verification step: 
    * Open the cockpit to monitor the VMs. 
      * In a web browser, go to https://kvm-host-IP-here:9090
      * Sign-in with your credentials set in the variables file
      * Enable administrative access in the top right.
      * Open the 'Virtual Machines' tab from the left side toolbar.
    * Sometimes it just takes a while, especially if it's lacking resources. Give it some time and then re-reun the playbook/role with [tags](vault-and-tags.md). 
    * If that doesn't work, SSH into the bastion as root ("ssh root@\<bastion-ip-address-here\>") and then run, "export KUBECONFIG=~/ocpinst/auth/kubeconfig" and then "oc whoami" and make sure it ouputs "system:admin". Then run the shell command from the role you would like to check on manually: i.e. 'oc get nodes', 'oc get co', etc.
    * Open the .openshift_install.log file for information on what happened and try to debug the issue.