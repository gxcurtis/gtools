# FreeIPA Ansible Roles

## IPA VARS

__NOTE:__ Verify variables associated with ipa_servers, forwarders, dns_servers, domain and realm

```yaml
# all.yml
ipa_domain: example.com
ipa_realm: "{{ ipa_domain | upper }}"
ipa_basedn: "{{ ipa_domain.split('.') | map('regex_replace', '^', 'dc=') | join(',') }}"

ipaadmin_password: "{{ vault_ipaadmin_password }}"
ipadm_password: "{{ vault_ipadm_password }}"

# IPA Servers

ipaserver_domain: "{{ ipa_domain }}"
ipaserver_realm: "{{ ipa_realm }}"
ipaserver_idstart: 60000
ipaserver_idmax: 69999
ipaserver_setup_adtrust: false
ipaserver_setup_kra: false
ipaserver_setup_dns: true
ipaserver_setup_ca: true
ipaserver_setup_firewalld: true
ipaserver_external_ca: false
ipaserver_no_reverse: false
ipaserver_auto_reverse: true

## Depends on deployment segmentation 
ipaserver_allow_zone_overlap: true
ipaserver_no_forwarders: true
ipaserver_auto_forwarders: false
ipaserver_no_host_dns: true # Unless another IPA server exists
ipaserver_forward_policy: only # Or first
ipaserver_forwarders: []

# IPA Replicas

## Must be FQDN of existing IPA servers or replicas, can't include self
ipareplica_servers: []

ipareplica_domain: "{{ ipa_domain }}"
ipareplica_realm: "{{ ipa_realm }}"
ipareplica_setup_adtrust: "{{ ipaserver_setup_adtrust }}"
ipareplica_setup_ca: "{{ ipaserver_setup_ca }}"
ipareplica_setup_kra: "{{ ipaserver_setup_kra }}"
ipareplica_setup_dns: "{{ ipaserver_setup_dns }}"
ipareplica_no_reverse: "{{ ipaserver_no_reverse }}"
ipareplica_auto_reverse: "{{ ipaserver_auto_reverse }}"
ipareplica_setup_firewalld: "{{ ipaserver_setup_firealld }}"

ipareplica_allow_zone_overlap: "{{ ipaserver_allow_zone_overlap }}"
ipareplica_no_forwarders: "{{ ipaserver_no_forwarders }}"
ipareplica_auto_forwarders: "{{ ipaserver_auto_forwarders }}"
ipareplica_no_host_dns: false # Should be able to resolve existing IPA server
ipareplica_forward_policy: "{{ ipaserver_forward_policy }}"
ipareplica_forwarders: "{{ ipaserver_forwarders }}"

# IPA Clients

## Must be FQDN of existing IPA servers or replicas
ipaclient_servers: "{{ ipa_servers }}"

ipaclient_domain: "{{ ipa_domain }}"
ipaclient_realm: "{{ ipa_realm }}"
ipaclient_setup_firewalld: true
ipaclient_force_join: false # Set to true if having issues
ipaclient_no_ntp: true
ipaclient_no_ssh: true
ipaclient_no_sshd: true
ipaclient_mkhomedir: true

# Need dns servers if configure resolver true
ipaclient_dns_servers: "{{ ipa_servers }}"
ipaclient_configure_dns_resolver: true
ipaclient_cleanup_dns_resolver: true
ipasssd_enable_dns_updates: true
```
