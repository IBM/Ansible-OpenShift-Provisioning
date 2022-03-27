
## Installation Instructions

### Setup
* **Step 1: Get This Repository**
    * In your terminal, navigate to a folder where you would like to store this project, copy/paste the following and hit Enter:
      ~~~
      git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git
      ~~~
* **Step 2: Get Red Hat Info**
    * In a web browser, navigate to the Red Hat [console](https://console.redhat.com/openshift/install/ibmz/user-provisioned) and copy the OpenShift pull secret and save it for the next step.
* **Step 3: Set Variables**
    * In a text editor of your choice, open [inventories/group_vars/all.yaml](env.yaml).
    * Fill out variables marked with `X` to match your specific installation. 
    * This is the most important step in the process. Take the time to make sure everything here is correct.
* **Step 4: Setup Script** 
    * Navigate to the folder where you cloned the Git Repository in your terminal.
    * Run this shell command:
      ~~~
      ansible-playbook playbooks/setup.yaml --ask-vault-pass
      ~~~

### Provisioning
* **Step 5: Running the Main Playbook** 
    * Navigate to the folder where you cloned the Git repository in your terminal.
    * Start the master playbook by running this shell command: 
      ~~~
      ansible-playbook playbooks/site.yaml --ask-vault-pass
      ~~~
    * Alternatively, move more carefully by running one playbook at a time. Here's the list of playbooks to be run in order, also found in [playbooks/site.yaml](playbooks/site.yaml):
        * create_kvm_host.yaml
        * setup_kvm_host.yaml
        * create_bastion.yaml
        * setup_bastion.yaml
        * create_nodes.yaml
        * ocp_verification.yaml
    * Watch Ansible as it completes the installation, correcting errors if they arise. 
    * To look at what is running in detail, open the playbook and/or roles/role-name/tasks/main.yaml
    * If the process fails in error:
      * Go through the steps in the [troubleshooting](#Troubleshooting) section. 
      * Use [tags](#Tags) to selectively start from a certain point in the playbook. Each role has a corresponding tag for convenience. For example, to run the httpd and get_ocp roles of the setup_bastion playbook: 
        ~~~
        ansible-playbook playbooks/setup_bastion.yaml --tags 'httpd,get_ocp' --ask-vault-pass
        ~~~

### Post-Install Complete 
* **Step 6: First-Time Login**
    * The last step of the main playbook will print a URL, username and temporary password for first-time login.
    * Use a web-browser to type in the URL, which should take you to a sign-in page. Use the provided credentials to sign in. You will have to bypass a warning screen.
    * Congratulations! Your OpenShift cluster installation is now complete.  

## Troubleshooting
If you encounter errors while running the main playbook, there are a few things you can do:
1) Double check your variables.
2) Inspect the part that failed by opening the playbook and/or roles at `roles/role_to_inspect/tasks/main.yaml`
3) Google the specific error message.
3) Re-run the role indivually with [tags](#Tags) or with the verbosity '-v' option to get more debugging information (more v's give more info). For example: 
    ~~~
    ansible-playbook main.yaml --tags get_ocp -vvv --ask-vault-pass
    ~~~
4) Teardown the KVM host with the delete_partition.yaml playbook or teardown troublesome KVM guests with the [teardown](#Teardown) playbooks.
6) E-mail Jacob Emery at jacob.emery@ibm.com
7) If it's a problem with an OpenShift verification step: 
  * Open the cockpit to monitor the VMs. 
    * In a web browser, go to https://kvm-host-IP-here:9090
    * Sign-in with your credentials set in the variables file
    * Enable administrative access in the top right.
    * Open the 'Virtual Machines' tab from the left side toolbar.
  * Sometimes it just takes a while, especially if it's lacking resources. Give it some time and then re-reun the playbook/role with [tags](#Tags). 
  * If that doesn't work, SSH into the bastion as root ("ssh root@bastion-ip-address-here") and then run, "export KUBECONFIG=~/ocpinst/auth/kubeconfig" and then "oc whoami" and make sure it ouputs "system:admin". Then run the shell command from the role you would like to check on manually: i.e. 'oc get nodes', 'oc get co', etc.
  * Open the .openshift_install.log file for information on what happened and try to debug the issue.

## Teardown: 
* If you would like to teardown your VMs, first determine whether you would like to do a `full`, `partial`, or `app` teardown, specified below.
  * `full`:
    * To teardown all the OpenShift KVM guest virtual machines (will not teardown KVM host) run:
      ~~~
      ansible-playbook playbooks/teardown.yaml --tags full --ask-vault-pass
      ~~~
  * `partial`: 
    * To teardown all OpenShift KVM guest virtual machines <i>except the bastion</i> (will also not teardown KVM host or extra RHEL app VMs) run:
      ~~~
      ansible-playbook teardown.yaml --tags partial
      ~~~ 
    * To start the main.yaml playbook back from that point, run:
      ~~~
      ansible-playbook main.yaml --tags 'get_ocp,create_nodes,verification'
      ~~~
* To teardown the KVM host, use the [delete_partition playbook](playbooks/delete_partition.yaml)
