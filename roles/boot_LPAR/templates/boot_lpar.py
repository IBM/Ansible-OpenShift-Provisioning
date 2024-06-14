from tessia.baselib.hypervisors.hmc import hmc
import logging
import argparse

def list_of_strings(arg):
    return arg.split(',')

parser = argparse.ArgumentParser(description="Get the environment.")

parser.add_argument("--cpcname", type=str, help="this is the CEC/CPC hosting the target LPAR" )
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
parser.add_argument("--livedisktype", type=str, help="Can be of type dasd or scsi", required=True, default='')
parser.add_argument("--devicenr", type=str, help="deviceenr for the live disk image")
parser.add_argument("--netset_ip", type=str, help="network setup ip for the live image")
parser.add_argument("--netset_gateway", type=str)
parser.add_argument("--netset_network_type", type=str, help="could be of type osa or pci")
parser.add_argument("--netset_network_device", type=str, help="network device id")
parser.add_argument("--netset_password", type=str, help="live disk password")
parser.add_argument("--netset_dns", type=list_of_strings, help="comma seperated list of dns addresss in order")
parser.add_argument("--livedisklun", type=str, help="Lun id when the disk type is scsi and will be na when disktype is dasd")
parser.add_argument("--livediskwwpn", type=str, help="wwpn id of the scsi disk and will be na when disktype is dasd")

parser.add_argument("--log_level", type=str, help="can be of type INFO or DEBUG")
args = parser.parse_args()



# cpc_name = "a46" # this is the CEC/CPC hosting the target LPAR
# hmc_address = "hmca2.boeblingen.de.ibm.com" # URL where HMC API is running
# hmc_user = ""
# hmc_password = ""
# Currently there are no parameters for instantiating a hmc hypervisor
hypervisor_params = None
hmc = hmc.HypervisorHmc(args.cpcname, args.hmchost,
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
lpar_name = args.lparname
lpar_cpu = args.cpu
lpar_memory = args.memory
lpar_parameters = {
    "boot_params": {
        "boot_method" : args.livedisktype.lower(),
        "devicenr": args.devicenr,
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
if args.livedisktype.lower()=="dasd" and args.livedisklun=="na" and args.livediskwwpn=="na":
    pass
elif args.livedisktype.lower()=="scsi" and args.livedisklun!="na" and args.livediskwwpn!="na":
    lpar_parameters["boot_params"]["lun"]=args.livedisklun
    lpar_parameters["boot_params"]["wwpn"]=args.livediskwwpn
else:
    raise Exception("Please check the live disk details")
hmc.start(lpar_name, lpar_cpu, lpar_memory, lpar_parameters)
hmc.logoff()

