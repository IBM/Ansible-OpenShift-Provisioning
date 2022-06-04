# Step 1: Get the Repository
* Open the terminal
    * On MacOS: cmd+space to open spotlight search, type in 'terminal' and hit enter  
* Navigate to a folder (AKA directory) where you would like to store this project. 
    * Either do so graphically, or use the command-line. 
    * Here are some helpful commands for doing so:
        * `pwd` to see what directory you're currently in
        * `ls` to list child directories
        * `cd <folder-name>` to change directories (`cd ..` to go up to the parent directory)
        * `mkdir <new-folder-name>` to create a new directory
* Copy/paste the following and hit enter:  
`git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git`
* Open the newly created folder (`cd`)
* All in all, it will look something like this:  
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
LICENSE		ansible.cfg	inventories	playbooks	vault.yaml
```
* All you need to run Ansible is a terminal and a text editor.
* However, an IDE like [VS Code](https://code.visualstudio.com/download) is highly recommended for an integrated, user-friendly experience with helpful extensions like [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).