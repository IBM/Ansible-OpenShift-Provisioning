import argparse
import json

def list_of_strings(arg):
    return arg.split(',')

parser = argparse.ArgumentParser(description="Get the environment.")

def rev_octet(ip):
    return '.'.join(ip.split('.')[:3][::-1])

parser.add_argument("--control_ips", type=list_of_strings,required=True)
parser.add_argument("--compute_ips", type=list_of_strings,required=True)
parser.add_argument("--bootstrap_ip",type=str,required=True)
parser.add_argument("--bastion_ip",type=str,required=True)
parser.add_argument("--control_names",type=list_of_strings,required=True)
parser.add_argument("--compute_names",type=list_of_strings,required=True)
parser.add_argument("--bootstrap_name",type=list_of_strings,required=True)

args = parser.parse_args()

rev_dns = {}
for i in range(len(args.control_ips)):
    rev_ip = rev_octet(args.control_ips[i])
    if rev_ip not in rev_dns:
        rev_dns[rev_ip] = []
    rev_dns[rev_ip].append([args.control_ips[i].split(".")[-1],args.control_names[i]])

for i in range(len(args.compute_ips)):
    rev_ip = rev_octet(args.compute_ips[i])
    if rev_ip not in rev_dns:
        rev_dns[rev_ip] = []
    rev_dns[rev_ip].append([args.compute_ips[i].split(".")[-1],args.compute_names[i]])

rev_ip_bastion = rev_octet(args.bastion_ip)
if rev_ip_bastion not in rev_dns:
    rev_dns[rev_ip_bastion]=[[args.bastion_ip.split(".")[-1],"bastion"]]
else:
    rev_dns[rev_ip_bastion].append([args.bastion_ip.split(".")[-1],"bastion"])
rev_dns[rev_ip_bastion].append([args.bastion_ip.split(".")[-1],"api"])
rev_dns[rev_ip_bastion].append([args.bastion_ip.split(".")[-1],"api-int"])

rev_ip_bootstrap = rev_octet(args.bootstrap_ip)
if rev_ip_bootstrap not in rev_dns:
    rev_dns[rev_ip_bootstrap]=[[args.bootstrap_ip.split('.')[-1],"bootstrap"]]
else:
    rev_dns[rev_ip_bootstrap].append([args.bootstrap_ip.split('.')[-1],"bootstrap"])

print(json.dumps(rev_dns))

