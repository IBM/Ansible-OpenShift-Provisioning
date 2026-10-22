from tessia.baselib.hypervisors.hmc import hmc
import logging
import argparse
import urllib3

def list_of_strings(arg):
    return arg.split(',')

parser = argparse.ArgumentParser(description="Get the environment.")

parser.add_argument("--cpcname", type=str, help="this is the CEC/CPC hosting the target LPAR")
parser.add_argument("--lparname", type=str, help="Hypervisor name", required=True)
parser.add_argument("--hmchost", type=str, help="HMC Hostname or IP, enter the hmc url here", required=True)
parser.add_argument("--hmcuser", type=str, help="HMC user", required=True)
parser.add_argument("--hmcpass", type=str, help="HMC user password", required=True)
parser.add_argument("--cpu", type=int, help="number of Guest CPUs", required=True)
parser.add_argument("--memory", type=int, help="Guest memory in MB", required=True)
parser.add_argument("--kernel", type=str, help="kernel URI", required=True, default='')
parser.add_argument("--cmdline", type=str, help="kernel cmdline", required=True, default='')
parser.add_argument("--initrd", type=str, help="Initrd URI", required=True, default='')

#live disk info
parser.add_argument("--dpm_enabled", type=str, help="True if CPC is dpm enabled", default='False')
parser.add_argument("--livediskuuid", type=str, help="UUID of the scsi device required for DPM lpars only", default='')
parser.add_argument("--livedisktype", type=str, help="Can be of type dasd or scsi", required=True, default='')
parser.add_argument("--devicenr", type=str, help="deviceenr for the live disk image", default='')
parser.add_argument("--netset_ip", type=str, help="network setup ip for the live image")
parser.add_argument("--netset_gateway", type=str)
parser.add_argument("--netset_network_type", type=str, help="could be of type osa or pci")
parser.add_argument("--netset_network_device", type=str, help="network device id")
parser.add_argument("--netset_password", type=str, help="live disk password")
parser.add_argument("--netset_dns", type=list_of_strings, help="comma seperated list of dns addresss in order")
parser.add_argument("--livedisklun", type=str, help="Lun id when the disk type is scsi and will be na when disktype is dasd", default='na')
parser.add_argument("--livediskwwpn", type=str, help="wwpn id of the scsi disk and will be na when disktype is dasd", default='na')

parser.add_argument("--status_timeout", type=int, help="Timeout in seconds waiting for LPAR load to reach operating status (default: 300)", default=300)
parser.add_argument("--log_level", type=str, help="can be of type INFO or DEBUG")
parser.add_argument("--deactivate_first", action="store_true", default=False,
                    help="Deactivate the LPAR if it is currently active before loading")
args = parser.parse_args()

# Example usage:
# cpc_name = "CPC_NAME" # this is the CEC/CPC hosting the target LPAR
# hmc_address = "hmc.example.com" # URL where HMC API is running
# hmc_user = "username"
# hmc_password = "password"
# Currently there are no parameters for instantiating a hmc hypervisor
hypervisor_params = None
hmc = hmc.HypervisorHmc(args.cpcname.upper() if args.cpcname else args.cpcname, args.hmchost,
                        args.hmcuser, args.hmcpass, hypervisor_params)

# enable below block for debug output
if args.log_level == "DEBUG":
    consoleHandler=logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    consoleHandler.setFormatter(formatter)
    hmc._logger.addHandler(consoleHandler)
    hmc._logger.setLevel(logging.DEBUG)
# We must be logged in before submitting any command.
hmc.login()

# Here we define the parameters of the guest to be started.
lpar_name = args.lparname.upper() if args.lparname else args.lparname
lpar_cpu = args.cpu
lpar_memory = args.memory
lpar_parameters = {
    "boot_params": {
        "boot_method": args.livedisktype.lower(),
        "status_timeout": args.status_timeout,
        'netsetup': {
            "mac": None,
            "ip": args.netset_ip,
            "mask": 16,
            "gateway": args.netset_gateway,
            "type": args.netset_network_type, # also accepts 'pci'
            "device": args.netset_network_device, # enter the function id when type is 'pci'
            "password": args.netset_password,
            "dns": args.netset_dns,
        },
        'netboot': {
            "cmdline": args.cmdline,
            "kernel_url": args.kernel,
            "initrd_url": args.initrd
        }
    }
}

def _strip_0x(val):
    """Strip leading '0x' or '0X' prefix (HMC API expects plain hex strings)."""
    return val[2:] if isinstance(val, str) and val.lower().startswith('0x') else val

if args.livedisktype.lower() == "dasd":
    if not args.devicenr:
        raise Exception("Please check the live disk details: devicenr is required for DASD")
    lpar_parameters["boot_params"]["devicenr"] = args.devicenr
elif args.livedisktype.lower() == "scsi":
    if not args.livedisklun or args.livedisklun == "na" or not args.livediskwwpn or args.livediskwwpn == "na":
        raise Exception("Please check the live disk details: lun and wwpn are required for SCSI")
    lpar_parameters["boot_params"]["lun"] = _strip_0x(args.livedisklun)
    lpar_parameters["boot_params"]["wwpn"] = _strip_0x(args.livediskwwpn)
    lpar_parameters["boot_params"]["devicenr"] = args.devicenr
    lpar_parameters["boot_params"]["uuid"] = args.livediskuuid
else:
    raise Exception(f"Unsupported livedisktype: {args.livedisktype}")
# Deactivate the LPAR before loading if it is currently running.
# This is required when reinstalling a cluster whose nodes are still active.
if args.deactivate_first:
    import zhmcclient
    import sys as _sys
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    _session = zhmcclient.Session(args.hmchost, args.hmcuser, args.hmcpass, verify_cert=False)
    try:
        _client = zhmcclient.Client(_session)
        _cpc = _client.cpcs.find(name=args.cpcname.upper() if args.cpcname else args.cpcname)
        _lpar = _cpc.lpars.find(name=lpar_name)
        _lpar.pull_full_properties()
        _status = _lpar.get_property('status')
        print(f"[deactivate_first] LPAR {lpar_name} current status: {_status}", file=_sys.stderr)
        if _status not in ('not-activated', 'not-operating'):
            print(f"[deactivate_first] Deactivating LPAR {lpar_name} (status={_status}) ...", file=_sys.stderr)
            _lpar.deactivate(wait_for_completion=True, force=True)
            print(f"[deactivate_first] LPAR {lpar_name} deactivated.", file=_sys.stderr)
        else:
            print(f"[deactivate_first] LPAR {lpar_name} already inactive (status={_status}), skipping.", file=_sys.stderr)
    finally:
        _session.logoff()

hmc.start(lpar_name, lpar_cpu, lpar_memory, lpar_parameters)
hmc.logoff()
