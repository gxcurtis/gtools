#!/usr/bin/env python3

template = """
lang en_US.UTF-8
keyboard --vckeymap=us --xlayouts='us'
timezone {{ ks_timezone | default('Etc/UTC') }} --utc 

{{ ks_install_type | default('text') }}
{{ ks_after_action | default('reboot') }}
firstboot --disable
eula --agreed

firewall --enable --ssh
selinux --enforcing
rootpw --iscrypted {{ ks_rootpw_hash }}
bootloader --iscrypted --password={{ ks_grub_pwhash }}

{% if ks_network.bootproto == 'static' %}
network --bootproto=static --device={{ ks_network.device }} --hostname={{ ks_network.hostname }} --ip={{ ks_network.ip }} --gateway={{ ks_network.gateway }} --netmask={{ ks_network.netmask }} --nameserver={{ ks_network.nameserver }} --activate 
{% else %}
network --bootproto=dhcp --device={{ ks_network.device }} --hostname={{ ks_network.hostname }} --activate
{% endif %}

{{ ks_install_source }}
{% for ks_repo in ks_repos %}
repo --name={{ ks_tepo.name }} --baseurl={{ ks_repo.baseurl }}
{% endfor %}

%include {{ ks_partfile }}

%packages

{% for package in ks_packages %}
{{ package }}
{% endfor %}

%end
"""
