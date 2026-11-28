# Fedora/RHEL System Role Certificate

## Requesting certificates

```yml
certificate_requests:
  - name: <SERVICE/HOST-NAME>
    dns: 
      - dns1.example.com
      - dns1
      - dns2.example.com
      - dns2
    ca: ipa # OR self-signed
    principal: <SERVICE>/<HOST_FQDN>@<IPA_REALM> # e.g., HTTP/webserver.example.com@EXAMPLE.COM
    auto_renew: true
    # run_before: command to run before cert renewal/install
    # run_after: command to run after cert renewal/install
```

## Managing client certificate trust store (ca-trust)

```yml
# from file
certificate_trust:
  - name: <CERT_NAME>
    src: /path/to/example.crt
    remote_src: true # if on managed host else false
    state: present

# from PEM string
certificate_trust:
  - name: <CERT_NAME>
    state: present
    content: |
      --- PEM FORMATTED CERT ---
      ... ... .... .... .... ... 
      --- PEM END CERTIFICATE---
```
