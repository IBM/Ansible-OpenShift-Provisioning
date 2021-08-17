# Ansible-OpenShift-Provisioning

The goal of this playbook is to setup and deploy an OpenShift cluster utilizing KVM as the virtualization method

Tags:
bastion = configuration of bastion for OCP
keymastr = ssh key configuration and testing
bastionvm = creation of Bastion KVM guest
boostrap = creation of Boostrap KVM guest
compute = creation of the Compute nodes KVM guests (2)
control = creation of the Control nodes KVM guests (3 min)
dns = configuration of dns server on bastion
setocp = download of OCP installer and http server configuration
haproxy = configuration of haproxy on bastion kvm guest
httpconf = configuration of httpd server on bastion kvm guest
kvmhost = tasks to apply to KVM host for OCP cluster
setocp = get ocp playbook

 
