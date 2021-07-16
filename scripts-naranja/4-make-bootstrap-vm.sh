#/bin/bash

. ./env

echo "using LOCATION: ${LOCATION}"

  virt-install --name bootstrap \
    --disk ${VIRT_IMAGE_DIR}/bootstrap.qcow2 --ram 16000 --cpu host --vcpus 4 \
    --os-type linux --os-variant rhel8.0 \
    --network network=${VIR_NET} --noreboot --wait -1 --graphics none --console pty,target_type=serial \
    --location ${LOCATION} \
    --extra-args "nomodeset console=ttyS0,115200n8 rd.neednet=1 coreos.inst=yes coreos.inst.install_dev=vda coreos.live.rootfs_url=${LOCATION}/${ROOTFS} ip=${BOOTSTRAP_IP}::${DEFAULT_GW}:${SUBNET_MASK}:bootstrap::none:1500 nameserver=${NAMESERVER} coreos.inst.ignition_url=${LOCATION}/ignitions/bootstrap.ign"
