#!/usr/bin/env bash
# shellcheck disable=SC2034
SCRIPT="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT")" && pwd -P)"

PNG_FILE="$SCRIPT_DIR/resources/graphics/tux-background.png"
FONT_FILE="$SCRIPT_DIR/resources/fonts/jetbrains-mono-16.pf2"
BOOTSTRAP_FILE="$SCRIPT_DIR/resources/grubmenus/bootstrap.cfg"

# Display help message with -h
print_help() {
    cat <<EOF

usage: $SCRIPT [OUTFILE]

OUTFILE = Output file of efi binary

options:
    -p [PNG_FILE] (Path to PNG background)
    -f [FONT_FILE] (Path to .pf2 font file)
    -b [BOOTSTRAP_CONFIG] (Path to embedded bootstrap grub config)
    -h (Print this help text)

EOF
}

# Set Options/Arguments
while getopts ':ho:b:p:f:' opt; do
    case "$opt" in
        o) OUT_FILE="$OPTARG" ;;
        b) BOOTSTRAP_FILE="$OPTARG" ;;
        p) PNG_FILE="$OPTARG" ;;
        f) FONT_FILE="$OPTARG" ;;
        h) print_help && exit 0 ;;
        :) printf 'Missing argument -%s\n' "$OPTARG" && exit 1 ;;
        \?) printf 'Invalid argument -%s\n' "$OPTARG" && exit 1 ;;
    esac
done

shift "$(( OPTIND - 1 ))"

OUTFILE="${1:-grubx64.efi}"
OUTFILE="${OUTFILE%.efi}.efi"

### Main ###
grub_mods=(
    normal
    linux
    efinet
    net
    tftp
    http
    png
    gfxterm
    font
    all_video
    part_gpt
    part_msdos
    fat
    xfs
    ext2
    diskfilter
    mdraid1x
    lvm
    search
    search_fs_uuid
    configfile
    loadenv
    echo
    ls
    test
    reboot
    halt
)

main() {
    grub2-mkstandalone \
        --format=x86_64-efi \
        --output="$OUTFILE" \
        --fonts="" \
        --themes="" \
        --locales="" \
        --modules="${grub_mods[*]}" \
        "files/background.png=$PNG_FILE" \
        "files/font.pf2=$FONT_FILE" \
        "boot/grub/grub.cfg=$BOOTSTRAP_FILE"

    chmod +x "$OUTFILE"

    return 0
}

main

