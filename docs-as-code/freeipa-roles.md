# FreeIPA Ansible Roles

## VARS

### IPA Shared Vars

```yaml
# all.yml
ipa_domain: example.com
ipa_realm: "{{ ipa_domain | upper }}"
ipa_basedn: "{{ ipa_domain.split('.') | map('regex_replace', '^', 'dc=') | join(',') }}"
ipa_servers: []

ipaadmin_password: "{{ ipa_vault_admin_password }}"
ipadm_password: "{{ ipa_vault_dm_password }}"

ipaclient_no_ntp: true
ipaclient_no_ssh: true
ipaclient_no_sshd: true
ipaclient_mkhomedir: true
ipasssd_enable_dns_updates: true
```
### IPA Server Vars

```yaml
# ipaservers.yml

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

# Depends on air gapped deployment

ipaserver_allow_zone_overlap: true
ipaserver_no_reverse: false
ipaserver_auto_reverse: true
ipaserver_no_forwarders: true
ipaserver_auto_forwarders: false
ipaserver_forward_policy: first # Or only
ipaserver_forwarders: []

```

### IPA Replica Vars

```yaml
# ipareplicas.yml

ipareplica_domain: "{{ ipa_domain }}"
ipareplica_realm: "{{ ipa_realm }}"
ipareplica_servers: "{{ ipa_servers }}"
ipareplica_setup_adtrust: false
ipareplica_setup_ca: true
ipareplica_setup_kra: false
ipareplica_setup_dns: true
ipareplica_no_reverse: false
ipareplica_auto_reverse: true
ipareplica_setup_firewalld: true

# Depends on air gapped deployment

ipareplica_no_forwarders: true
ipareplica_auto_forwarders: false
ipareplica_allow_zone_overlap: false
ipareplica_no_host_dns: true
```

### FreeIPA Client Vars

```yaml
# ipaclients.yml

ipaclient_domain: "{{ ipa_domain }}"
ipaclient_realm: "{{ ipa_realm }}"
ipaclient_dns_servers: "{{ ipa_dns_servers }}"
ipaclient_servers: "{{ ipa_servers }}"
ipaclient_setup_firewalld: true
ipaclient_force_join: true

ipaclient_configure_dns_resolver: true
ipaclient_cleanup_dns_resolver: true
```
