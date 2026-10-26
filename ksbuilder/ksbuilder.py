#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from getpass import getpass
from ipaddress import IPv4Interface
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

try:
    from pykickstart.parser import KickstartParser
    from pykickstart.version import makeVersion, versionMap
    from pykickstart.errors import KickstartError

    kickstart_versions = versionMap.keys() if isinstance(versionMap, dict) else versionMap

    fedora_versions = sorted([vers for vers in kickstart_versions if vers.startswith("F") and not vers.startswith("FC")], reverse=True, key=lambda x: int(x.lstrip("F")))

    rhel_versions = sorted([vers for vers in kickstart_versions if vers.startswith("RHEL")], reverse=True, key=lambda x: int(x.lstrip("RHEL")))

    latest_versions = fedora_versions[:3] + rhel_versions[:3]
        
    validation_available = True
except ImportError:
    validation_available = False

# For relative execution
SCRIPT_DIR = Path(__file__).resolve().parent

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", nargs="?", type=argparse.FileType("r"), default=None, help="Json file or '-' to read from stdin")
    parser.add_argument("-o", "--output", dest="outfile", help="Output file path")
    parser.add_argument("-l", "--list-defaults", nargs="*", choices=kickstart_defaults.keys(), metavar="KEY", help="Print defaults for specifed parameters, or all parameters if omitted")
    parser.add_argument("--stig", action="store_true", help="Use defaults with additional STIG inputs")
    parser.add_argument("--storage", choices=["auto","standard","raid1","dynamic"], default="dynamic", help="Specify a storage configuration strategy")
    parser.add_argument("--hostname", help="Set hostname")
    parser.add_argument("--ip", help="Set IPv4 address in CIDR notation")
    parser.add_argument("--gateway", help="Set IPv4 gateway")
    parser.add_argument("--timezone", help="Set timezone")
    parser.add_argument("--packages", nargs='*',  help="Specify packages to add")
    parser.add_argument("--root-password", nargs="?", const=True, metavar="ROOT_PASSWORD_HASH", help="Encrypted ROOT password hash or leave blank to be prompted")
    parser.add_argument("--grub-password", nargs="?", const=True, metavar="GRUB_PASSWORD_HASH", help="Encrypted GRUB password hash or leave blank to be prompted")
    parser.add_argument("--luks-password", nargs="?", const=True, help="Plaintext LUKS password or leave blank to be prompted")
    parser.add_argument("--user-passwords", action="store_true", help="Prompt for users defined in kickstat")
    parser.add_argument("--interface-type", nargs=1, choices=["graphical", "text", "cmdline"], help="Specify interface type during installation")
    parser.add_argument("--after-install", nargs=1, choices=["reboot", "poweroff", "shutdown", "halt"], help="Specify system action after installion ends")

    if validation_available:
        parser.add_argument(
            "-v",
            "--validate",
            dest="versions",
            nargs="*",
            choices=kickstart_versions,
            help="Validate generated kickstart syntax and compatability" 
        )

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    return parser.parse_args()

def prompt_password(account):
    attempts = 0
    while True:
        if attempts >= 3:
            print("Too many failed attempts. Exiting...")
            sys.exit(1)
        first_input = getpass(f"Enter password for {account}: ")
        second_input = getpass(f"Confirm {account} password: ")
        if first_input == second_input:
            password = first_input
            print()
            return password
        else:
            print("Passwords do not match! Try again...", end="\n\n")
            attempts += 1
        
def hash_password(password, grub=False):
    password = password.strip()

    if grub:
        command = ["grub2-mkpasswd-pbkdf2"]
        password = f"{password}\n{password}\n"
    else:
        command = ["openssl", "passwd", "-6", "-stdin"]
    
    try:
        result = subprocess.run(command, input=password, capture_output=True, text=True, check=True)
    except TypeError:
        result = subprocess.run(command, input=password, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
        
    if grub:
        match = re.search(r"grub\.pbkdf2\.sha512\.\d+\.[0-9A-Fa-f]+\.[0-9A-Fa-f]+", result.stdout)

        hashed_password = match.group()
    else:
        hashed_password = result.stdout

    return hashed_password.strip()

def parse_cidr_ip(cidr_ip):
    cidr_ip = cidr_ip.strip()
    interface = IPv4Interface(cidr_ip)

    return str(interface.ip), str(interface.netmask)

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
            
def render_kickstart_template(ksdata: dict, outfile=None, template="kickstart.ks.j2"):
    env = Environment(
        loader=FileSystemLoader(f"{SCRIPT_DIR}/templates"),
        undefined=StrictUndefined,
        keep_trailing_newline=True
    )

    template = env.get_template(template)
    
    rendered_kickstart = template.render(**ksdata)

    if outfile is None:
        sys.stdout.write(rendered_kickstart)
    else:
        with open(outfile, "w") as f:
            f.write(rendered_kickstart)

    return rendered_kickstart

def calc_min_storage(storage: dict):
    min_storage = storage["boot_size"] + storage["boot_efi_size"]

    for lv in storage["lvm"]["logvols"]:
        min_storage += lv["size"]
    
    return min_storage

def add_stig_defaults(ksdata: dict):
        ksdata["bootloader"]["args"] += ["fips=1","audit=1","audit_backlog_limit=8192"]
        ksdata["bootloader"]["superuser"] = "bootadmin"
        ksdata["bootloader"]["password"] = hash_password("install", grub=True)
        ksdata["timesource"]["servers"] += ["time.nist.gov"]
        ksdata["network"]["ipv6"]["enabled"] = False
        ksdata["network"]["nameservers"] += ["9.9.9.9","8.8.8.8","1.1.1.1"]
        ksdata["firewall"]["system_defaults"] = False
        ksdata["storage"]["luks_passphrase"] = "install"
        ksdata["openscap"]["hardening"] = True

# Default Kickstart Values
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
    "after_install": "reboot",
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
        "locked": False,
        "password": hash_password("install")
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
            "password": hash_password("install"),
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
    "storage": {
        "configuration": "dynamic",
        "template": "storage.j2",
        "includefile": "/tmp/part-include",
        "luks_passphrase": "",
        "boot_efi_size": 600,
        "boot_size": 1024,
        "min_size": 0,
        "max_size": 2 * pow(1024, 2),
        "growth_percent": 80,
        "lvm": {
            "vgname": "os",
            "logvols": [
                {
                    "mount": "/",
                    "name": "root",
                    "size": 20480,
                    "fstype": "xfs"
                },
                {
                    "mount": "/home",
                    "name": "home",
                    "size": 10240,
                    "fstype": "xfs"
                },
                {
                    "mount": "/scratch",
                    "name": "scratch",
                    "size": 2048,
                    "fstype": "xfs"
                },
                {
                    "mount": "/tmp",
                    "name": "tmp",
                    "size": 2048,
                    "fstype": "xfs"
                },
                {
                    "mount": "/var",
                    "name": "var",
                    "size": 2048,
                    "fstype": "xfs"
                },
                {
                    "mount": "/var/tmp",
                    "name": "vartmp",
                    "size": 2048,
                    "fstype": "xfs"
                },
                {
                    "mount": "/var/log",
                    "name": "varlog",
                    "size": 2048,
                    "fstype": "xfs"
                },
                {
                    "mount": "/var/log/journal",
                    "name": "journal",
                    "size": 2048,
                    "fstype": "xfs"
                },
                {
                    "mount": "/var/log/audit",
                    "name": "audit",
                    "size": 2048,
                    "fstype": "xfs"
                },
                {
                    "mount": "swap",
                    "name": "swap",
                    "size": 4096,
                    "fstype": "swap"
                }
            ]
        }
    },
    "openscap": {
        "hardening": False,
        "content_type": "scap-security-guide",
        "profile": "xccdf_org.ssgproject.content_profile_stig"
    },
    "software": {
        "ignore_missing": True,
        "ignore_broken": False,
        "weak_deps": True,
        "repos": [
            {
            "name": "",
            "baseurl": "",
            "install": True
            }
        ],
        "core_packages": [
            "@core",
            "curl",
            "tmux",
            "rsync",
            "openssl",
            "vim-enhanced",
            "bash-completion",
            "info",
            "man-db",
            "man-pages"
        ],
        "packages": [
            "git",
            "tcpdump",
            "nmap-ncat",
            "bind-utils",
            "nfs-utils",
            "python3",
            "python3-pip",
            "ansible-core",
            "openscap-scanner",
            "scap-security-guide",
            "policycoreutils-python-utils",
        ]
    },
    "pre_ks_templates": [],
    "post_ks_templates": []
}

### Main ###
if __name__ == '__main__':
    args = build_parser()

    if args.stig:
        add_stig_defaults(kickstart_defaults)

    if args.list_defaults is not None:
        list_default_parameters(args.list_defaults, kickstart_defaults)
        sys.exit(0)

    if args.json_file:
        with args.json_file as f:
            inputs = json.load(f)     
        ksdata = merge_kickstart_data(inputs, kickstart_defaults)
    elif not sys.stdin.isatty():
        inputs = json.load(sys.stdin)
        ksdata = merge_kickstart_data(inputs, kickstart_defaults)
    else:
        ksdata = kickstart_defaults

    ### Set calculated minimum disk size 
    ksdata["storage"]["min_size"] = calc_min_storage(ksdata["storage"])

    if args.storage is not None:
        ksdata["storage"]["configuration"] = args.storage

    if args.hostname is not None:
        ksdata["network"]["hostname"] = args.hostname
        
    if args.ip is not None:
        ip, netmask = parse_cidr_ip(args.ip)
        ksdata["network"]["ipv4"]["address"] = ip
        ksdata["network"]["ipv4"]["netmask"] = netmask
        ksdata["network"]["bootproto"] = "static"

    if args.gateway is not None:
        ksdata["network"]["gateway"] = args.gateway

    if args.timezone is not None:
        ksdata["timezone"] = args.timezone
        
    if args.root_password is not None:
        if args.root_password is True:
            rootpw = prompt_password("root")
            rootpw = hash_password(rootpw)
        else:
            rootpw = args.root_password

        ksdata["rootpw"]["password"] = rootpw

    if args.grub_password is not None:
        if args.grub_password is True:
            grubpw = prompt_password("grub")
            grubpw = hash_password(grubpw, grub=True)
        else:
            grubpw = args.grub_password
        ksdata["bootloader"]["password"] = grubpw

    if args.luks_password is not None:
        if args.luks_password is True:
            lukspw = prompt_password("luks")
        else:
            lukspw = args.luks_password
        ksdata["partition"]["luks_passphrase"] = lukspw

    if args.user_passwords:
        for i, user in enumerate(ksdata["users"]):
            if not user["password"]:
                userpw = prompt_password(user["name"])
                userpw = hash_password(userpw)
                ksdata["users"][i]["password"] = userpw

    if args.packages is not None:
        ksdata["software"]["packages"] = args.packages

    if args.interface_type is not None:
        ksdata["interface_type"] = args.interface_type

    if args.after_install is not None:
        ksdata["after_install"] = args.after_install

    kickstart = render_kickstart_template(ksdata, outfile=args.outfile)

    if validation_available:
        if args.versions is not None:
            if args.versions != []:
                versions = args.versions
            else:
                versions = latest_versions

            tmp_file = ksdata["storage"]["includefile"]

            render_kickstart_template(ksdata, outfile=tmp_file, template="storage.j2")

            print("Validation Summary")
            print("------------------")
            for version in versions:
                try:
                    ksparser = KickstartParser(makeVersion(version))            
                    ksparser.readKickstartFromString(kickstart)

                    print(f"Valid kickstart for {version.replace('F','Fedora')}")

                except KickstartError as exc:
                    print(f"Invalid Kickstart for {version.replace('F','Fedora')}:\n{exc}")

            if Path(tmp_file).exists():
                Path(tmp_file).unlink()

