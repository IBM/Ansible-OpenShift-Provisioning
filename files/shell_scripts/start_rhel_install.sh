#!bin/bash
virt-install --connect qemu:///system --name bastion --memory 4096 --vcpus 2 --disk size=20 --cdrom /var/lib/libvirt/images/rhel83.iso
--accelerate --import --network network=macvtap-net --extra-args "ip=9.60.87.139::9.60.86.1:255.255.255.0:bastion.distribution.ocpz.wsclab.endicott.ibm.com::none nameserver=9.60.70.82 vnc vncpassword=12341234 inst.repo=hd:/dev/vda ipv6.disable=1" --location /rhcos-install --qemu-commandline="-drive if=none,id=ignition,format=raw,file=/var/lib/libvirt/images/rhel83.iso,readonly=on -device virtio-blk,serial=ignition,drive=ignition" --noautoconsole
