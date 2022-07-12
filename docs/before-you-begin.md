# Before You Begin
## Description
* This project automates the User-Provisioned Infrastructure (UPI) method for deploying Red Hat OpenShift Container Platform (RHOCP) on IBM zSystems / LinuxONE using Kernel-based Virtual Machine (KVM) as the hypervisor.
## Support
* This is an unofficial project created by IBMers.
* This installation method is not officially supported by either Red Hat or IBM.
* However, once installation is complete, the resulting cluster is supported by Red Hat. UPI is the only supported method for RHOCP on IBM zSystems.
## Difficulty
* This process is much easier than doing so manually, but still not an easy task. You will likely encounter errors, but you will reach those errors quicker and understand the problem faster than if you were doing this process manually. After using these playbooks once, successive deployments will be much easier.
    * A very basic understanding of what Ansible does is recommended. Advanced understanding is helpful for further customization of the playbooks. 
    * A basic understanding of the command-line is required.
    * A basic understanding of git is recommended, especially for creating your organization's own fork of the repository for further customization.
    * An advanced understanding of your computing environment is required for setting the environment variables.
* These Ansible Playbooks automate a User-Provisioned Infrastructure (UPI) deployment of Red Hat OpenShift Container Platform (RHOCP). This process, when done manually, is extremely tedious, time-consuming, and requires high levels of Linux AND IBM zSystems expertise. 
* UPI is currently the only supported method for deploying RHOCP on IBM zSystems.
## Why Free and Open-Source?
* <u>Trust</u>:
    * IBM zSystems run some of the most highly-secure workloads in the world. Trust is paramount. 
    * Developing and using code transparently builds trust between developers and users, so that users feel safe using it on their highly sensitive systems. 
* <u>Customization</u>:
    * IBM zSystems exist in environments that can be highly complex and vary drastically from one datacenter to another.
    * Using code that isn't in a proprietary black box allows you to see exactly what is being done so that you can change any part of it to meet your specific needs.
* <u>Collaboration</u>:
    * If users encounter a problem, or have a feature request, they can get in contact with the developers directly.
    * Submit an issue or pull request on GitHub or email jacob.emery@ibm.com. 
    * Collaboration is highly encouraged!
* <u>Lower Barriers to Entry</u>:
    * The easier it is to get RHOCP on IBM zSystems up and running, the better - for you, IBM and Red Hat!
    * It is free because RHOCP is an incredible product that should have the least amount of barriers to entry as possible. 
    * The world needs open-source, private, and hybrid cloud.