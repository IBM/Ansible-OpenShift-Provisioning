#!bin/bash

##create
qemu-img create -f qcow2 -F qcow2 -b /var/lib/libvirt/images/rhcos-qemu.s390x.qcow2 /var/lib/libvirt/images/bootstrap.qcow2 100G

##boot
virt-install --boot kernel=rhcos-kernel,initrd=rhcos-initramfs.img,kernel_args='rd.neednet=1
coreos.inst.install_dev=/dev/vda coreos.live.rootfs_url=http://<bastion_IP>:8080/bin/rhcos-rootfs.img
coreos.inst.ignition_url=http://<bastion_IP>:8080/ignition/bootstrap.ign ip=<bootstrap_IP>::<gateway>:<netmask>:::none
nameserver=<bastion_IP>’ --connect qemu:///system --name bootstrap --memory 16384 --vcpus 4 --disk /var/lib/libvirt/
images/bootstrap.qcow2 --accelerate --import --network network=macvtap-net --qemu-commandline="-drive
if=none,id=ignition,format=raw,file=/var/www/html/ignition/bootstrap.ign,readonly=on -device virtio-
blk,serial=ignition,drive=ignition"


