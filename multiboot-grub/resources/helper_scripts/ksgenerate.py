#!/usr/bin/env python3
import argparse
from pathlib import Path
from textwrap import dedent

# DEFAULT HASHES (CHANGE ME)
rhash = '$6$GJ9/UjQ/wGaPDfbe$dYYw4RcBmAtm51sTCHFCPObRPhXbbVp.sRw1/CyrJm7NSCaaAo6CgQMAkhxThzRr4O1Hw1kynGM.snoW3feuR.'
ghash = 'grub.pbkdf2.sha512.10000.505CDD3B289AE7C8A96A7177086DE19795DA667245A949F47D7C6DB437AAE2DAD60947F35708A50AA36A3273A67B9CF072C112E4EEABE837C51357C53CD9FD87.7DA1F5861E24F6728A8C453B0703A74914297B1CC86E801F168DE3E2BE6AD69B5827F0B27AB74378EA16B112A294981BB0A6403E9313B524C6B1381696B2922E'

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', type=str, default='localhost', help="Set hostname")
    parser.add_argument('-t', '--timezone', type=str, default='Etc/UTC', help='Set timezone')
    parser.add_argument('-i', '--installation-type', choices=['text', 'graphical', 'cmdline'], default='text', help='Set installation type')
    parser.add_argument('-x', '--after-action', choices=['halt', 'reboot', 'poweroff', 'shutdown'], default='reboot', help='Set action to perform after kickstart')
    parser.add_argument('-n', '--network', choices=['static','dhcp'], default='dhcp', help='Configure network')
    parser.add_argument('-r', '--rootpw', type=str, default=rhash, help='Set root password hash')
    parser.add_argument('-g', '--grubpw', type=str, default=ghash, help='Set grub password hash')
    parser.add_argument('-d', '--repos', action='store_true')
    parser.add_argument('-p', '--packages-file', type=Path, default=Path('packages-default'), help='Include packages from file')
    parser.add_argument('-b', '--pre-file', type=Path, default=Path('pre-default'), help='Include kickstart %%pre section from file')
    parser.add_argument('-a', '--post-file', type=Path, default=Path('post-default'), help='Include kickstart %%post section from file')
    parser.add_argument('-k', '--kickstart-include', type=str, default='/tmp/partition-scheme', help='Add kickstart %%include directives')

    return parser.parse_args()

def network_settings(args):
    network_command = f"network --bootproto={args.network} --hostname={args.hostname} --activate"

    if args.network == 'static':
        ip = input("Enter static IP: ")
        gateway = input("Enter gateway IP: ")
        netmask = input("Enter netmask: ")

        network_command += f" --ip={ip} --gateway={gateway} --netmask={netmask}"
    
    return network_command

def assemble_kickstart(args):
    pre_content = args.pre_file.read_text()
    packages_content = args.packages_file.read_text()
    post_content = args.post_file.read_text()

    main_content = dedent(f"""\
        lang en_US.UTF-8
        keyboard --vckeymap=us --xlayouts='us'
        timezone {args.timezone} --utc 
        
        {args.installation_type}
        {args.after_action}
        firstboot --disable
        eula --agreed

        {network_settings(args)}

        firewall --enable --ssh
        selinux --enforcing
        rootpw --iscrypted {args.rootpw}

        bootloader --append="console=tty0 console=ttyS0,115200n8" --iscrypted --password={args.grubpw}

        %include {args.kickstart_include}

    """)

    content = main_content + packages_content + pre_content + post_content
    return content
    

if __name__ == '__main__':
    args = build_parser()
    kickstart = assemble_kickstart(args)

    if args.hostname == 'localhost':
        ksfile="default.ks"
    else:
        ksfile=f"{args.hostname}.ks"

    with open(f"../kickstarts/{ksfile}", "w") as f:
        f.write(kickstart)


