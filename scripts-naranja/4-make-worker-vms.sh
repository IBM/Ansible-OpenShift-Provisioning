#/bin/bash

. ./env

echo "LOCATION: ${LOCATION}"

  virt-install --name worker1 \
    --disk ${VIRT_IMAGE_DIR}/worker1.qcow2 --ram 32000 --cpu host --vcpus 8 \
    --os-type linux --os-variant rhel8.0 \
    --network network=${VIR_NET} --noreboot --wait -1 --graphics none --console pty,target_type=serial \
    --location ${LOCATION} \
    --extra-args "nomodeset console=ttyS0,115200n8 rd.neednet=1 coreos.inst=yes coreos.inst.install_dev=vda coreos.live.rootfs_url=${LOCATION}/${ROOTFS} ip=${WORKER1_IP}::${DEFAULT_GW}:${SUBNET_MASK}:worker1::none:1500 nameserver=${NAMESERVER} coreos.inst.ignition_url=${LOCATION}/ignitions/worker.ign"

  virt-install --name worker2 \
    --disk ${VIRT_IMAGE_DIR}/worker2.qcow2 --ram 32000 --cpu host --vcpus 8 \
    --os-type linux --os-variant rhel8.0 \
    --network network=${VIR_NET} --noreboot --wait -1 --graphics none --console pty,target_type=serial \
    --location ${LOCATION} \
    --extra-args "nomodeset console=ttyS0,115200n8 rd.neednet=1 coreos.inst=yes coreos.inst.install_dev=vda coreos.live.rootfs_url=${LOCATION}/${ROOTFS} ip=${WORKER2_IP}::${DEFAULT_GW}:${SUBNET_MASK}:worker2::none:1500 nameserver=${NAMESERVER} coreos.inst.ignition_url=${LOCATION}/ignitions/worker.ign"

  virt-install --name worker3 \
    --disk ${VIRT_IMAGE_DIR}/worker3.qcow2 --ram 32000 --cpu host --vcpus 8 \
    --os-type linux --os-variant rhel8.0 \
    --network network=${VIR_NET} --noreboot --wait -1 --graphics none --console pty,target_type=serial \
    --location ${LOCATION} \
    --extra-args "nomodeset console=ttyS0,115200n8 rd.neednet=1 coreos.inst=yes coreos.inst.install_dev=vda coreos.live.rootfs_url=${LOCATION}/${ROOTFS} ip=${WORKER3_IP}::${DEFAULT_GW}:${SUBNET_MASK}:worker3::none:1500 nameserver=${NAMESERVER} coreos.inst.ignition_url=${LOCATION}/ignitions/worker.ign"
