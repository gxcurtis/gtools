#!/usr/bin/env bash

rdp() {
    local OPTIND=1
    local OPTARG opt
    local user="$(whoami)"
    local domain='example.com'
    local image=freerdp:3
    
    while getopts ':u:d:h:' opt; do
        case "$opt" in
            u) user="$OPTARG"
            ;;
            d) domain="$OPTARG"
            ;;
            h) host="$OPTARG"
            ;;
            :) printf 'Missing argument: -%s' "$OPTARG"; return 2
            ;;
            \?) printf 'Invalid option: -%s' "$OPTARG"; return 2
            ;;
        esac
    done

    shift $(( OPTIND - 1))

    local host="$1"
    if [[ -z $host ]]; then
        printf 'Missing host argument.\nusage: rdp <HOSTNAME>\n'
        return 1
    fi

    podman run --rm -it -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix "$image" /v:"$host" /u:"$user" /d:"$domain" /sec:nla /cert:ignore +clipboard /size:80% /dynamic-resolution /from-stdin:force /log-level:ERROR 
}

