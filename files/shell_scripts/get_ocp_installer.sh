#!bin/bash

##get and extract mirror 1
wget https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/latest/openshift-client-linux.tar.gz
tar -xvzf openshift-client-linux.tar.gz

##get and extract mirror 2
wget https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/latest/openshift-install-linux.tar.gz
tar -xvzf openshift-client-linux.tar.gz

##Make executable
chmod +x kubectl oc openshift_install

##move installed to bin folder
mv kubectl oc openshift_install /usr/local/bin/
