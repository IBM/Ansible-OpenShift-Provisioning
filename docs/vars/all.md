# Step 2: Set Variables - All
These variables apply to all hosts defined in Ansible inventory.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**ansible_ssh_private_key_file** | Absolute path to the private SSH key on your Ansible controller to be used for connecting to hosts. | /home/user/.ssh/id_rsa
**rh_username** | Red Hat username. | redhat.user
**rh_pass** | Password to above Red Hat user's account. | rEdHatPa$s!
**rh_pull_secret** | Pull secret for above Red Hat user. | {"auths":{"cloud.openshift<br />.com":{"auth":"b3Blb<br />...<br />4yQQ==","email":"redhat.<br />user@gmail.com"}}}
**timezone** | Desired timezone for VMs using 'TZ database' (Area/City) format. | America/New_York
**language** | Desired locale identifier for VMs. | en_US.UTF-8
**keyboard** | Desired keyboard mapping, find options with <br />'localectl list-locales' command | us
**proxy_env.http_proxy** | (Optional) A proxy URL to use for creating HTTP connections outside the cluster. Will be<br /> used in the install-config and applied to other Ansible hosts unless set otherwise in<br /> no_proxy below. Must follow this pattern: http://username:pswd>@ip:port | http://ocp-admin:Pa$sw0rd@9.72.10.1:80
**proxy_env.https_proxy** | (Optional) A proxy URL to use for creating HTTPS connections outside the cluster. Will be<br /> used in the install-config and applied to other Ansible hosts unless set otherwise in<br /> no_proxy below. Must follow this pattern: https://username:pswd@ip:port | https://ocp-admin:Pa$sw0rd@9.72.10.1:80
**proxy_env.no_proxy** | (Optional) A comma-separated list (no spaces) of destination domain names, IP<br /> addresses, or other network CIDRs to exclude from proxying. When using a<br /> proxy, all necessary IPs and domains for your cluster will be added automatically. See<br /> roles/get_ocp/templates/install-config.yaml.j2 for more details on the template. <br />Preface a domain with . to match subdomains only. For example, .y.com matches<br /> x.y.com, but not y.com. Use * to bypass the proxy for all listed destinations. | example.com,192.168.10.1
**ocp_download_url** | Base URL to be combined with next two vars for downloading OpenShift. Must end with '/'. | https://mirror.openshift.com/pub/openshift-v4/multi/clients/ocp/4.13.1/s390x/
**ocp_client_tgz** | Name of OpenShift client file to be downloaded. | openshift-client-linux.tar.gz
**ocp_install_tgz** | Name of OpenShift install file to be downloaded. | openshift-install-linux.tar.gz
**rhcos_download_url** | Base URL to be combined with the next three vars for downloading CoreOS files. Must end with '/'. | https://mirror.openshift.com/pub/openshift-v4/s390x/dependencies/rhcos/4.12/4.12.3/
**rhcos_live_kernel** | Name of CoreOS live kernel file to be downloaded. | rhcos-4.12.3-s390x-live-kernel-s390x
**rhcos_live_initrd** | Name of CoreOS live initial ram disk file to be downloaded. | rhcos-4.12.3-s390x-live-initramfs.s390x.img
**rhcos_live_rootfs** | Name of CoreOS live root file system file to be downloaded. | rhcos-4.12.3-s390x-live-rootfs.s390x.img
**os_variant** | Version of RHEL closest to desired CoreOS version. | rhel8.6
**metadata_name** | Overarching name for OpenShift cluster, used in many plases. | ocp_na_east
**base_domain** | Base domain for the cluster, will be combined with metadata_name to create cluster URL. | ihost.com