# Step 1: Get Info
## Get Repository
* Open the terminal  
* Navigate to a folder (AKA directory) where you would like to store this project. 
    * Either do so graphically, or use the command-line. 
    * Here are some helpful commands for doing so:
        * `pwd` to see what directory you're currently in
        * `ls` to list child directories
        * `cd <folder-name>` to change directories (`cd ..` to go up to the parent directory)
        * `mkdir <new-folder-name>` to create a new directory
* Copy/paste the following and hit enter:  
`git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git`
* Change into the newly created directory
* The commands and output should resemble the following example:  
```
$ pwd
/Users/example-user
$ mkdir ansible-project
$ cd ansible-project/
$ git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git
Cloning into 'Ansible-OpenShift-Provisioning'...
remote: Enumerating objects: 3472, done.
remote: Counting objects: 100% (200/200), done.
remote: Compressing objects: 100% (57/57), done.
remote: Total 3472 (delta 152), reused 143 (delta 143), pack-reused 3272
Receiving objects: 100% (3472/3472), 506.29 KiB | 1.27 MiB/s, done.
Resolving deltas: 100% (1699/1699), done.
$ ls
Ansible-OpenShift-Provisioning
$ cd Ansible-OpenShift-Provisioning/
$ ls
CHANGELOG.md	README.md	docs		mkdocs.yaml	roles
LICENSE		ansible.cfg	inventories	playbooks	
```
## Get Pull Secret
* In a web browser, navigate to Red Hat's [Hybrid Cloud Console](https://console.redhat.com/openshift/install/ibmz/user-provisioned), click the text that says 'Copy pull secret' and save it for the next step.
## Gather Environment Information
* You will need a lot of information about the environment this cluster will be set-up in. 
* You will need the help of at least your IBM zSystems infrastructure team so they can provision you a storage group. You'll also need them to provide you with
* IP address range, hostnames, subnet, gateway, how much disk space you have to work with, etc.
* A full list of variables needed are found on the next page. Many of them are filled in with defaults or are optional.
* Please take your time. I would recommend having someone on stand-by in case you need more information or need to ask a question about the environment.