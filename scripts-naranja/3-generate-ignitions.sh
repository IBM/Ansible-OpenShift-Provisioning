#!/bin/bash

rm -rf ignitions
mkdir -p ignitions
cp install-config.yaml ignitions

# create kubernetes manifests
openshift-install create manifests --dir=./ignitions

# ensure masters are not schedulable
sed -i 's/mastersSchedulable: true/mastersSchedulable: false/g' ignitions/manifests/cluster-scheduler-02-config.yml

# create ignition config files
openshift-install create ignition-configs --dir=./ignitions

# copy ign files to http server directory
cp ./ignitions/*.ign /var/www/html/ocp/ignitions

# setting permissions in http server directory for binaries and ignitions
chmod -R 777 /var/www/html/ocp
