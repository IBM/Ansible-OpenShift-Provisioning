#!/usr/bin/env python3
from tessia.baselib.hypervisors.zvm.zvm import HypervisorZvm
import argparse

parser = argparse.ArgumentParser(description="Get the environment.")

parser.add_argument("--zvmname", type=str, help="z/VM Hypervisor name", required=True)
parser.add_argument("--zvmhost", type=str, help="z/VM Hostname or IP", required=True)
parser.add_argument("--zvmuser", type=str, help="z/VM user", required=True)
parser.add_argument("--zvmpass", type=str, help="z/VM user password", required=True)
parser.add_argument("--cpu", type=int, help="number of Guest CPUs", required=True)
parser.add_argument("--memory", type=int, help="Guest memory in MB", required=True)
parser.add_argument("--kernel", type=str, help="kernel URI", required=True, default='')
parser.add_argument("--cmdline", type=str, help="kernel cmdline", required=True, default='')
parser.add_argument("--initrd", type=str, help="Initrd URI", required=True, default='')
parser.add_argument("--network", type=str, help="Network mode for zvm nodes Supported modes: OSA, vswitch, RoCE , Hipersockets", required=True)

args = parser.parse_args()

parameters = {
            'transfer-buffer-size': 8000
    }

interfaces=[]
if args.network.lower() == 'osa' or args.network.lower() == 'hipersockets':
    interfaces=[{ "type": "osa", "id": "{{ hypershift.agents_parms.zvm_parameters.nodes[item].interface.subchannels.split(',') | map('regex_replace', '0.0.', '') | join(',') }}"}]

elif args.network.lower() == 'roce':
    interfaces=[{ "type": "pci", "id": "{{ hypershift.agents_parms.zvm_parameters.nodes[item].interface.ifname }}"}]

guest_parameters = {
"boot_method": "network",
"storage_volumes" : [],
"ifaces" : interfaces,
"netboot": {
        "cmdline": args.cmdline,
        "kernel_uri": args.kernel,
        "initrd_uri": args.initrd,
        }
}

zvm = HypervisorZvm(args.zvmname,args.zvmhost, args.zvmuser, args.zvmpass, parameters)
zvm.login()
print("Logged in ")
zvm.start(args.zvmuser, args.cpu, args.memory, guest_parameters)
print("VM Started")
zvm.logoff()
print("Logged out")
