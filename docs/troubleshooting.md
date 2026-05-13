# Troubleshooting
If you encounter errors while running the main playbook, there are a few things you can do:

* Double check your variables.
* Inspect the part that failed by opening the playbook or role at roles/role-name/tasks/main.yaml
* Google the specific error message.
* Re-run the role with the verbosity '-v' option to get more debugging information (more v's give more info). For example:
```
ansible-playbook playbooks/setup_bastion.yaml -vvv
```
* Use tags
  * To be more selective with what parts of a playbook are run, use tags.
  * To determine what part of a playbook you would like to run, open the playbook you'd like to run and find the roles parameter. Each [role](https://github.com/IBM/Ansible-OpenShift-Provisioning/tree/main/roles) has a corresponding tag.
  * There are also occasionally tags for sections of a playbook or within the role themselves.
  * This is especially helpful for troubleshooting. You can add in tags under the `name` parameter for individual tasks you'd like to run.
  * Here's an example of using a tag:
```
ansible-playbook playbooks/setup_kvm_host.yaml --tags "section_2,section_3"
```
  * This runs only the parts of the [setup_kvm_host playbook](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml) marked with tags section_2 and section_3. To use more than one tag, they must be quoted (single or double) and comma-separated (with or without spaces between).

## Specialized Troubleshooting Guides

For specific scenarios, refer to these detailed troubleshooting guides:

### Disconnected Installation Issues

* **[DNS Configuration for Disconnected Mirroring](disconnected-dns-configuration.md)** - Resolves DNS issues when the bastion needs internet access for mirroring but DNS service isn't configured yet
* **[Internet Access Troubleshooting](troubleshooting-disconnected-internet-access.md)** - Step-by-step guide for fixing connectivity issues when bastion cannot reach mirror.openshift.com
* **[oc-mirror "No Release Images Found" Error](troubleshooting-oc-mirror-no-release-images.md)** - Fixes version specification issues and helps find available OpenShift versions
* **[oc-mirror Timeout Issues](troubleshooting-oc-mirror-timeout.md)** - Configure appropriate timeouts for large mirroring operations to prevent "async task did not complete" errors
* **[Monitoring OC-Mirror Progress](monitoring-oc-mirror-progress.md)** - Real-time monitoring of image mirroring to see which images are being pulled

### Common Disconnected Scenarios

**Problem**: Downloads fail with "Could not find or access file" or "Temporary failure in name resolution"
**Solution**: See [Internet Access Troubleshooting](troubleshooting-disconnected-internet-access.md) and [DNS Configuration](disconnected-dns-configuration.md)

**Problem**: oc-mirror reports "no release images found"
**Solution**: See [oc-mirror Troubleshooting](troubleshooting-oc-mirror-no-release-images.md)

**Problem**: Mirroring times out with "async task did not complete within the requested time"
**Solution**: See [oc-mirror Timeout Configuration](troubleshooting-oc-mirror-timeout.md)

**Problem**: Want to see which images are being mirrored in real-time
**Solution**: See [Monitoring OC-Mirror Progress](monitoring-oc-mirror-progress.md)

**Problem**: Bastion has IP forwarding but still can't reach internet
**Solution**: Check DNS configuration in [DNS Configuration Guide](disconnected-dns-configuration.md)

## Inventory Naming Conflicts

**Problem**: Ansible connects to the bastion with the controller username instead of the configured [`ansible_user`](inventories/default/hosts), and verbose SSH output shows `ESTABLISH SSH CONNECTION FOR USER: None`.

**Cause**: The inventory defines both a group named [`[bastion]`](inventories/default/hosts) and a host named [`bastion`](inventories/default/hosts). This creates an ambiguous inventory pattern. When a play targets [`bastion`](inventories/default/hosts), Ansible can resolve the host pattern to the host object instead of the intended group member, which may result in missing effective connection variables and SSH falling back to the controller username.

**Symptoms**:
* [`ansible-inventory --graph`](ansible.cfg) prints `Found both group and host with same name: bastion`
* Verbose playbook output shows `ESTABLISH SSH CONNECTION FOR USER: None`
* SSH then authenticates as the local controller user instead of the expected remote user

**Resolution**:
* Do not define a host named [`bastion`](inventories/default/hosts)
* Keep a unique inventory hostname such as [`bastion-test`](inventories/default/hosts)
* If the same machine must belong to multiple groups, add the same unique host to both groups instead of creating a second host alias with the name [`bastion`](inventories/default/hosts)
* Use unambiguous play targets such as the actual host name or a dedicated group like [`mirrorhost`](inventories/default/hosts)

**Example**:
```ini
[bastion]
bastion-spyre ansible_host=9.47.88.74 ansible_user=wxa

[mirrorhost]
bastion-spyre
```

A validation was added to [`playbooks/0_setup.yaml:13`](playbooks/0_setup.yaml:13) so the setup playbook now fails early when a host named [`bastion`](inventories/default/hosts) is present in the inventory.

## General Troubleshooting

* E-mail Amadeus Podvratnik pod@de.ibm.com
* If it's a problem with an OpenShift verification step: 
    * Open the cockpit to monitor the VMs. 
      * In a web browser, go to https://kvm-host-IP-here:9090
      * Sign-in with your credentials set in the variables file
      * Enable administrative access in the top right.
      * Open the 'Virtual Machines' tab from the left side toolbar.
    * Sometimes it just takes a while, especially if it's lacking resources. Give it some time and then re-reun the playbook/role with tags.
    * If that doesn't work, SSH into the bastion as root ("ssh root@\<bastion-ip-address-here\>") and then run, "export KUBECONFIG=/root/ocpinst/auth/kubeconfig" and then "oc whoami" and make sure it ouputs "system:admin". Then run the shell command from the role you would like to check on manually: i.e. 'oc get nodes', 'oc get co', etc.
    * Open the .openshift_install.log file for information on what happened and try to debug the issue.