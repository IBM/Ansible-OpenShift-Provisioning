
#!/bin/bash
systemctl enable --now libvirtd
systemctl status libvirtd.service
systemctl status libvirtd
