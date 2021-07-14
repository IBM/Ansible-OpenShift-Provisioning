#!bin/bash
virsh console bootstrap
journalctl -u bootkube.service
