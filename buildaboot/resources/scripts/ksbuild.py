#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

# For relative execution
SCRIPT_DIR = Path(__file__).resolve().parent

# Dictionary of Default Kickstart Values
kickstart_defaults = {
    "lang": "en_US.UTF-8",
    "keyboard": {
        "vckeymap": "us",
        "xlayouts": "us"
    },
    "timezone": "Etc/UTC",
    "timesource": {
        "ntp_disable": False,
        "servers": [],
        "pools": []
    },
    "interface_type": "text",
    "system_action": "reboot",
    "eula": "agreed",
    "firstboot": "disable",
    "firewall": {
        "enabled": True,
        "system_defaults": True,
        "ssh": True,
        "http": False,
        "ftp": False,
        "smtp": False,
        "ports": [],
        "services": []
    },
    "network": {
        "bootproto": "dhcp",
        "hostname": "",
        "device": "link",
        "activate": True,
        "ipv4": {
            "enabled": True,
            "address": "",
            "gateway": "",
            "netmask": "",
            "dns_search": "",
            "auto_dns": True
        },
        "ipv6": {
            "enabled": True,
            "address": "",
            "gateway": "",
            "dns_search": "",
            "auto_dns": True
        },
        "no_defroute": False,
        "no_dns": False,
        "nameservers": [],
        "mtu": 1500,
        "bond": {
            "slaves": [],
            "opts": []
        },
        "vlan": {
            "id": 0,
            "interface_name": ""
        },
        "bridge": {
            "slaves": [],
            "opts": []
        }
    },
    "logging": {
        "host": "",
        "port": ""
    },
    "selinux": "enforcing",
    "rootpw": {
        "iscrypted": True,
        "locked": True,
        "password": ""
    },
    "bootloader": {
        "location": "mbr",        
        "args": [
            "console=tty0",
            "console=ttyS0,115200n8"
        ],
        "iscrypted": True,
        "password": "",
        "superuser": "root"
    },
    "users": [
        {
            "name": "ansible",
            "password": "",
            "iscrypted": True,
            "homedir": "/home/ansible",
            "shell": "/bin/bash",
            "gecos": "Ansible Admin",
            "groups": ["wheel"],
            "sshkey": ""
       }  
    ],
    "groups": [],
    "services": {
        "enabled": ["sshd"],
        "disabled": []
    },
    "partition": {
        "template": "pre-storage-script.j2",
        "tmpfile": "/tmp/part-include",
        "vgname": "os",
        "swap": True,
        "crypt_passphrase": ""
    },
    "openscap": {
        "hardening": False,
        "content_type": "scap-security-guide",
        "profile": "xccdf_org.ssgproject.content_profile_stig"
    },
    "packages": {
        "list": [
            "@core",
            "git",
            "curl",
            "tmux",
            "rsync",
            "chrony",
            "openssl",
            "tcpdump",
            "nmap-ncat",
            "vim-enhanced",
            "bash-completion",
            "openscap-scanner",
            "scap-security-guide",
            "authselect",
            "python3",
            "python3-pip",
            "ansible-core",
            "policycoreutils-python-utils",
            "bind-utils",
            "yum-utils",
            "nfs-utils",
            "info",
            "man-db",
            "man-pages"
        ],
        "ignore_missing": True,
        "ignore_broken": False,
        "weak_deps": True
    },
    "pre_ks_templates": [],
    "post_ks_templates": ["default-post-ks.j2"]
}

stig_defaults = {
    "timesource": {
        "servers": ["192.168.100.140","192.168.100.150"]
    },
    "firewall": {
        "system_defaults": False
    },
    "network": {
        "bootproto": "static",
        "hostname": "secure-server",
        "ipv4": {
            "address": "192.168.100.2",
            "gateway": "192.168.100.1",
            "netmask": "255.255.255.0"
        },
        "ipv6": {
            "enabled": False
        },
        "nameservers": [
            "192.168.100.110",
            "192.168.100.120"
        ]
    },
    "logging": {
        "host": "192.168.100.130"
    },
    "selinux": "enforcing",
    "rootpw": {
        "locked": True,
        "password": "$6$.SS2UVORxKkqgCio$Qq4lcZ12NuM8KyvBxo2J3a2xATCuB4t4V57ncBet.QModGGAkE1MacUR5t6M4XK1a2fKghPJPJh/OOEboh9uL."
    },
    "bootloader": {
        "args": [
             "console=tty0",
             "console=ttyS0,115200n8",
             "audit=1",
             "audit_backlog_limit=8192",
             "fips=1"
        ],
        "password": "grub.pbkdf2.sha512.10000.3AA73CFC245DFD2C0B8E10840D278084F66440AB0EE4E94D6D314BACD5F1387ED1BA1BF05B805ADE228CF08AAFE031E016CFC92D23F4A370CCE3D36DC184F61D.CB376E8D7AFF39EF47A9CDE03834EFE4538F5948662F0A8F9CAE17D234176F1B7524F957EB61A0EA6B6982285E1D7C29C38EF1CA78855AC31D90BDDF4495959A",
        "superuser": "bootadmin"
    },
    "users": [
        {
            "name": "ansible",
            "password": "$6$9IEt/2bU694XYO9.$QPnCJgSg/52ToX7C0/hcQ/9dCVVzKSB4VCLZJSGswv.JHh6udUXf1r.QRFgCSzyTWGHirvab4QeWCZUjQNAJw1",
            "iscrypted": True,
            "gecos": "Ansible Admin",
            "groups": ["wheel"],
            "sshkey": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFpAKkLrA1BNUJGSfGtbLr6YsC0FpXttI3dB5M25JJla"
        }
    ],
    "partition": {
        "crypt_passphrase": "install"
    },
    "openscap": {
        "hardening": True,
        "content_type": "scap-security-guide",
        "profile": "xccdf_org.ssgproject.content_profile_stig"
    },
    "post_ks_templates": ["post-hardening-script.j2"]
} 

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", dest="outfile", type=str, help="Output file path")
    parser.add_argument("json_file", nargs="?", type=Path, help="Path to JSON file for inputs")
    parser.add_argument("-s", "--stig", action="store_true", help="Use defaults with additional STIG inputs")
    parser.add_argument("-l", "--list-defaults", nargs="*", choices=kickstart_defaults.keys(), metavar="KEY", help="Print defaults for specifed sections, or all sections if omitted")
    parser.add_argument("--hostname", type=str, help="Set hostname") 
    parser.add_argument("--ip", type=str, help="Set IPv4 address") 

    args = parser.parse_args()

    return args

def list_default_parameters(requested_defaults: list, ksdefaults: dict):
    keys = requested_defaults or ksdefaults.keys()
    selected = {key: ksdefaults[key] for key in keys}
    print(json.dumps(selected, indent=3))

def merge_kickstart_data(ksinputs: dict, ksdefaults: dict):
    kickstart_data = ksdefaults
    kickstart_inputs = ksinputs

    for key, value in kickstart_inputs.items():
        if isinstance(kickstart_data.get(key), dict) and isinstance(value, dict):
            merge_kickstart_data(value, kickstart_data[key])
        else:
            kickstart_data[key] = value

    return kickstart_data
            
def render_kickstart(ksdata: dict, outfile=None):
    env = Environment(
        loader=FileSystemLoader(f"{SCRIPT_DIR}/templates"),
        undefined=StrictUndefined,
        keep_trailing_newline=True
    )

    template = env.get_template("kickstart.ks.j2")
    
    rendered_kickstart = template.render(**ksdata)

    if outfile is None:
        sys.stdout.write(rendered_kickstart)
    else:
        with open(outfile, "w") as f:
            f.write(rendered_kickstart)

if __name__ == '__main__':
    args = build_parser()

    if args.stig:
        defaults = merge_kickstart_data(stig_defaults, kickstart_defaults)
    else:
        defaults = kickstart_defaults

    if args.list_defaults is not None:
        list_default_parameters(args.list_defaults, defaults)
        sys.exit(0)

    if args.json_file:
        with open(args.json_file, "r") as f:
            inputs = json.load(f)     
        ksdata = merge_kickstart_data(inputs, defaults)
    else:
        ksdata = defaults

    if args.hostname is not None:
        ksdata["network"]["hostname"] = args.hostname
        
    if args.ip is not None:
        ksdata["network"]["ipv4"]["address"] = args.ip

    render_kickstart(ksdata, outfile=args.outfile)

