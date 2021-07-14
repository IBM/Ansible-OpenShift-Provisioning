#!bin/bash
virsh net-create macvtap.xml
virsh net-start --network macvtap-net
virsh net-autostart --network macvtap-net
virsh net-list --all
