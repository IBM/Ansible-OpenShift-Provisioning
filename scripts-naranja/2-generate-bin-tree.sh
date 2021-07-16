#!/bin/bash

. ./env

# create ocp and ignitions directories in http server
mkdir -p /var/www/html/ocp/ignitions

# copy binaries to http server directory
cp /root/ocpbin/rhcos-live-initramfs.s390x.img  /var/www/html/${CLUSTER_NAME}/${INITRAMFS}
cp /root/ocpbin/rhcos-live-kernel-s390x /var/www/html/${CLUSTER_NAME}/${KERNEL}
cp /root/ocpbin/rhcos-live-rootfs.s390x.img /var/www/html/${CLUSTER_NAME}/${ROOTFS}

#generating  .treeinfo file to be read by --location parameter
cat << EOF >> /var/www/html/${CLUSTER_NAME}/.treeinfo
[general]
arch = ${ARCHITECTURE}
family = Red Hat CoreOS
platforms = ${ARCHITECTURE}
version = ${OCP_RELEASE}
[images-${ARCHITECTURE}]
initrd = ${INITRAMFS}
kernel = ${KERNEL}
EOF
