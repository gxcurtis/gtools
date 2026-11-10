#!/usr/bin/env bash
set -euo pipefail

DISTRO='rhel'
VERSION='9'
REPO_PATH="$PWD"
REPO_SERVER=''
REPO_BASEURL="http://$REPO_SERVER"

PARALLEL_COUNT='5'
CONFIG_FILE=''

TUNNEL_HOST="$REPO_SERVER"
TUNNEL_SRC_PORT='localhost:8000'

if [[ -d "/repos" ]]; then
    REPO_PATH=/repos
fi

print_help() {
    cat <<EOF

usage: sync-repos [-h] [-v VERSION] [-t TUNNEL_HOST] [-s TUNNEL_SRC_PORT] [-r REPO_SERVER] [-R] [-f CONFIG_FILE] [-P PARALLEL_COUNT] [SUBURL...]

Args:
- DISTRO=$DISTRO
- VERSION=$VERSION
- TUNNEL_HOST=$TUNNEL_HOST
- TUNNEL_SRC_PORT=$TUNNEL_SRC_PORT
- REPO_SERVER=$REPO_SERVER
- REPO_BASEURL=$REPO_BASEURL
- REPO_PATH=$REPO_PATH
- CONFIG_FILE=$CONFIG_FILE
- PARALLEL_COUNT=$PARALLEL_COUNT

EOF

exit 0
}

while getopts ':hRv:t:s:r:p:f:P' opt; do
    case "$opt" in
        h) print_help ;;
        R) DISTRO='rocky' ;;
        v) VERSION="$OPTARG" ;;
        t) TUNNEL_HOST="$OPTARG" ;;
        s) TUNNEL_SRC_PORT="$OPTARG" ;;
        r) REPO_SERVER="$OPTARG" ;;
        p) REPO_PATH="$OPTARG" ;;
        f) CONFIG_FILE="$OPTARG" ;;
        P) PARALLEL_COUNT="$OPTARG" ;;
        :) printf 'Missing argument -%s' "$OPTARG" ;;
        \?) printf 'Invalid argument -%s' "$OPTARG" ;;
    esac
done

shift "$(( OPTIND - 1 ))"

test -n $DISTRO || DISTRO='rhel'
test -n $VERSION || VERSION='9'
test -n $REPO_PATH || REPO_PATH="$PWD"
test -n $REPO_SERVER || echo "ERROR: no repo server is defined" ; exit 1
REPO_BASEURL="http://$REPO_SERVER"

PARALLEL_COUNT='5'
CONFIG_FILE=''

test -n $TUNNEL_HOST || TUNNEL_HOST="$REPO_SERVER"
test -n $TUNNEL_HOST || TUNNEL_SRC_PORT='localhost:8000'

if [[ -d "/repos" ]]; then
    REPO_PATH=/repos
fi

if [[ -z "$CONFIG_FILE" ]]; then
    CONFIG_FILE="${DISTRO}${VERSION}.repo"
fi

if [[ "$TUNNEL_HOST" != "$REPO_SERVER" && -n "$TUNNEL_HOST" ]]; then
    REPO_BASEURL="http://$TUNNEL_SRC_PORT/rolling"
fi

if [[ "$VERSION" == '7' ]]; then
    REPO_SUBURLS=($DISTRO/$VERSION/server-{els-optional-rpms,els-rpms,extras})
    REPO_SUBURLS+=("fedora-epel/$VERSION/x86_64")
else
    REPO_SUBURLS=($DISTRO/$VERSION/{AppStream,BaseOS,CodeReadyBuilder}/x86_64)
    REPO_SUBURLS+=("fedora-epel/$VERSION/Everything/x86_64")
fi

if [[ $TUNNEL_HOST == $REPO_SERVER || -z $TUNNEL_HOST ]]; then
    SSH_TUNNEL="${TUNNEL_SRC_PORT}:localhost:80"
    TUNNEL_HOST="$REPO_SERVER"
else
    SSH_TUNNEL="${TUNNEL_SRC_PORT}:${REPO_SERVER}:80"
fi

cat <<EOF> "$CONFIG_FILE"
# Tunnel reposync commands
# ssh -S $HOME/.ssh/reposync-tunnel.sock -o ExitOnForwardFailure=yes -N -L $SSH_TUNNEL $TUNNEL_HOST
# dnf reposync --config $CONFIG_FILE --download-path $REPO_PATH --download-metadata
# ssh -S $HOME/.ssh/reposync-tunnel.sock -O exit $TUNNEL_HOST 2>/dev/null

[main]
retries=5
timeout=15
max_parallel_downloads=$PARALLEL_COUNT
reposdir=/dev/null
EOF

if [[ "$#" -gt 0 ]]; then
    REPO_SUBURLS+=("$@")
fi

for url in "${REPO_SUBURLS[@]}"; do
    IFS='/' read -ra parts <<< "$url"

    for part in "${parts[@]}"; do
        case "$part" in
            x86_64) continue ;;
            Everything) continue ;;
            os) continue ;;
            "$DISTRO") continue ;;
            "$VERSION") continue ;;
            *) REPO_ID="${part,,}" && break ;;
        esac    
    done

    cat <<EOF>> "$CONFIG_FILE"

[$REPO_ID-${DISTRO}${VERSION}]
name=${REPO_ID^^} ${DISTRO^^} ${VERSION}
baseurl=$REPO_BASEURL/$url
enabled=1
gpgcheck=0
gpgkey=0
EOF
done

if [[ "$TUNNEL_HOST" != "$REPO_SERVER" && -n "$TUNNEL_HOST" ]]; then
    socket="/tmp/.ssh-tunnel.sock"

    cleanup_tunnel() {
        echo "Cleaning up tunnel socket: $socket"
        ssh -S "$socket" -O exit "$TUNNEL_HOST" 2> /dev/null
    }
     
    trap cleanup_tunnel EXIT
    
    echo "Tunneling reposync through: $SSH_TUNNEL"
    ssh -S "$socket" -o ExitOnForwardFailure=yes -f -N -L "$SSH_TUNNEL" "$TUNNEL_HOST"
    
fi

echo "Starting reposync using $CONFIG_FILE and downloading to $REPO_PATH"
sleep 3

dnf reposync --config "$CONFIG_FILE" --download-path "$REPO_PATH" --download-metadata

