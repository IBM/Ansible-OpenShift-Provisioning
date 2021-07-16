#/bin/bash

. ./env

echo "LOCATION: ${LOCATION}"

  virt-install --name master1 \
    --disk ${VIRT_IMAGE_DIR}/master1.qcow2 --ram 16000 --cpu host --vcpus 4 \
    --os-type linux --os-variant rhel8.0 \
    --network network=${VIR_NET} --noreboot --wait -1 --graphics none --console pty,target_type=serial \
    --location ${LOCATION} \
    --extra-args "nomodeset console=ttyS0,115200n8 rd.neednet=1 coreos.inst=yes coreos.inst.install_dev=vda coreos.live.rootfs_url=${LOCATION}/${ROOTFS} ip=${MASTER1_IP}::${DEFAULT_GW}:${SUBNET_MASK}:master1::none:1500 nameserver=${NAMESERVER} coreos.inst.ignition_url=${LOCATION}/ignitions/master.ign"

  virt-install --name master2 \
    --disk ${VIRT_IMAGE_DIR}/master2.qcow2 --ram 16000 --cpu host --vcpus 4 \
    --os-type linux --os-variant rhel8.0 \
    --network network=${VIR_NET} --noreboot --wait -1 --graphics none --console pty,target_type=serial \
    --location ${LOCATION} \
    --extra-args "nomodeset console=ttyS0,115200n8 rd.neednet=1 coreos.inst=yes coreos.inst.install_dev=vda coreos.live.rootfs_url=${LOCATION}/${ROOTFS} ip=${MASTER2_IP}::${DEFAULT_GW}:${SUBNET_MASK}:master2::none:1500 nameserver=${NAMESERVER} coreos.inst.ignition_url=${LOCATION}/ignitions/master.ign"

  virt-install --name master3 \
    --disk ${VIRT_IMAGE_DIR}/master3.qcow2 --ram 16000 --cpu host --vcpus 4 \
    --os-type linux --os-variant rhel8.0 \
    --network network=${VIR_NET} --noreboot --wait -1 --graphics none --console pty,target_type=serial \
    --location ${LOCATION} \
    --extra-args "nomodeset console=ttyS0,115200n8 rd.neednet=1 coreos.inst=yes coreos.inst.install_dev=vda coreos.live.rootfs_url=${LOCATION}/${ROOTFS} ip=${MASTER3_IP}::${DEFAULT_GW}:${SUBNET_MASK}:master3::none:1500 nameserver=${NAMESERVER} coreos.inst.ignition_url=${LOCATION}/ignitions/master.ign"
