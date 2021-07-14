#!bin/bash
wget https://mirror.openshift.com/pub/openshift-v4/s390x/dependencies/rhcos/latest/latest/rhcos-qemu.s390x.qcow2.gz
dnf install -y gzip
gunzip rhcos-qemu.s390x.qcow2.gz /var/lib/libvirt/images/
