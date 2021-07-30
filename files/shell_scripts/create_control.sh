#!/bin/bash

qemu-img create -f qcow2 -b /var/lib/libvirt/images/rhcos-qemu.s390x.qcow2 /var/lib/libvirt/images/control-0.qcow2 100G
qemu-img create -f qcow2 -b /var/lib/libvirt/images/rhcos-qemu.s390x.qcow2 /var/lib/libvirt/images/control-1.qcow2 100G
qemu-img create -f qcow2 -b /var/lib/libvirt/images/rhcos-qemu.s390x.qcow2 /var/lib/libvirt/images/control-2.qcow2 100G

virt-install --boot kernel=rhcos-kernel,initrd=rhcos-initramfs.img,kernel_args='rd.neednet=1 coreos.inst.install_dev=/dev/vda coreos.live.rootfs_url=http://9.60.>
virt-install --boot kernel=rhcos-kernel,initrd=rhcos-initramfs.img,kernel_args='rd.neednet=1 coreos.inst.install_dev=/dev/vda coreos.live.rootfs_url=http://9.60.>
virt-install --boot kernel=rhcos-kernel,initrd=rhcos-initramfs.img,kernel_args='rd.neednet=1 coreos.inst.install_dev=/dev/vda coreos.live.rootfs_url=http://9.60.>
