# Install Gitlab Enterprise Edition and Runner

## Gitlab-EE

```sh
sudo dnf install -y curl policycoreutils openssh-server perl

curl -fsSL https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.rpm.sh -o /tmp/gitlab-repo.sh

sudo bash /tmp/gitlab-repo.sh

sudo EXTERNAL_URL="https://gitlab.example.com" dnf install -y gitlab-ee
```

Replace gitlab.example.com with internal fully qualified domain name (FQDN).

## Gitlab Runner

```sh
### Installation

curl -fsSL https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh -o /tmp/runner-repo.sh

sudo bash /tmp/runner-repo.sh

sudo dnf install -y gitlab-runner

sudo systemctl enable --now gitlab-runner

### Register

sudo gitlab-runner register \
    --url https://gitlab.example.com \
    --token glrt-XXXXXXXX \
    --executor shell

### Configuration

/etc/gitlab-runner/config.toml
```

