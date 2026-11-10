while getopts ':h' opt; do
    case "$opt" in
        h) printf 'HELP: Add options!\n' ;;
        :) printf 'Missing argument -%s\n' "$OPTARG" && exit 1 ;;
        \?) printf 'Invalid argument -%s\n' "$OPTARG" && exit 1 ;;
    esac
done

shift "$(( OPTIND - 1 ))"

