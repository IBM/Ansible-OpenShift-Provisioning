#!bin/bash

##install HTTP
dnf install -y httpd

##make folders
mkdir /var/www/html/bin /var/www/html/bootstrap

##get mirror 1
wget https://mirror.openshift.com/pub/openshift-v4/s390x/dependencies/rhcos/latest/latest/rhcos-4.7.7-s390x-live-kernel-s390x-O /var/www/html/bin/rhcos-kernel

##get mirror 2
wget https://mirror.openshift.com/pub/openshift-v4/s390x/dependencies/rhcos/latest/latest/rhcos-4.7.7-s390x-live-initramfs.s390x.img -O /var/www/html/bin/rhcos-initramfs.img

##get mirror 3
wget https://mirror.openshift.com/pub/openshift-v4/s390x/dependencies/rhcos/latest/latest/rhcos-4.7.7-s390x-live-rootfs.s390x.img -O rhcos-rootfs.img

##enable http
systemctl enable --now httpd; systemctl status httpd
