#!/usr/bin/env bash
# shellcheck disable=SC2034
SCRIPT="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT")" && pwd -P)"

# Display help message with -h
print_help() {
    cat <<EOF

usage: $SCRIPT

options:
    -h (Print this help text)

EOF
}

# Set Options/Arguments
while getopts ':h' opt; do
    case "$opt" in
        h) print_help && exit 0 ;;
        :) printf 'Missing argument -%s\n' "$OPTARG" && exit 1 ;;
        \?) printf 'Invalid argument -%s\n' "$OPTARG" && exit 1 ;;
    esac
done

shift "$(( OPTIND - 1 ))"

### Main ###

main() {
    exit 0
}

main

