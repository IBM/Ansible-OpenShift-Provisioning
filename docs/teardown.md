# Teardown: 
* If you would like to teardown your VMs, first determine whether you would like to do a `full` or `partial` teardown, specified below.
  * <u>Full Teardown</u>:
    * To teardown all the OpenShift KVM guest virtual machines (will not teardown KVM host) run:
```
ansible-playbook playbooks/teardown.yaml --tags full --ask-vault-pass
```
  * <u>Partial Teardown</u>: 
    * To teardown all OpenShift KVM guest virtual machines <i>except the bastion</i> (will also not teardown KVM host) run:
```
ansible-playbook playbooks/teardown.yaml --tags partial --ask-vault-pass
``` 
* To teardown the KVM host, use the [delete_partition playbook](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/delete_partition.yaml).
