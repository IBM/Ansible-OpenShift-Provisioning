# Troubleshooting
If you encounter errors while running the main playbook, there are a few things you can do:  

* Double check your variables.  
* Inspect the part that failed by opening the playbook or role at roles/role-name/tasks/main.yaml  
* Google the specific error message.  
* Re-run the role with the verbosity '-v' option to get more debugging information (more v's give more info). For example:  
```
ansible-playbook playbooks/4_create_bastion.yaml -vvv
```
* Use tags
  * To be more selective with what parts of a playbook are run, use tags. 
  * To determine what part of a playbook you would like to run, open the playbook you'd like to run and find the roles parameter. Each [role](https://github.com/IBM/Ansible-OpenShift-Provisioning/tree/main/roles) has a corresponding tag.
  * There are also occasionally tags for sections of a playbook or within the role themselves.
  * This is especially helpful for troubleshooting. You can add in tags under the `name` parameter for individual tasks you'd like to run. 
  * Here's an example of using a tag:
```
ansible-playbook playbooks/3_setup_hypervisors.yaml --tags 'section_2,section_3'
```
  * This runs only the parts of the [setup_hypervisor playbook](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_hypervisors.yaml) marked with tags section_2 and section_3. To use more than one tag, they must be quoted (single or double) and comma-separated (with or without spaces between).
* E-mail Jacob Emery at jacob.emery@ibm.com
* If it's a problem with an OpenShift verification step: 
    * Open the cockpit to monitor the VMs. 
      * In a web browser, go to https://hypervisor-IP-here:9090
      * Sign-in with your credentials set in the variables file
      * Enable administrative access in the top right.
      * Open the 'Virtual Machines' tab from the left side toolbar.
    * Sometimes it just takes a while, especially if it's lacking resources. Give it some time and then re-reun the playbook/role with tags.
    * If that doesn't work, SSH into the bastion as root ("ssh root@\<bastion-ip-address-here\>") and then run, "export KUBECONFIG=/root/ocpinst/auth/kubeconfig" and then "oc whoami" and make sure it ouputs "system:admin". Then run the shell command from the role you would like to check on manually: i.e. 'oc get nodes', 'oc get co', etc.
    * Open the .openshift_install.log file for information on what happened and try to debug the issue.