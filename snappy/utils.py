import subprocess

def run(*args, capture=True, check=True **kwargs):
    if capture:
        if sys.version_info >= (3,8):
            kwargs["capture_output"] = True
            kwargs["text"] = True
        else:
            kwargs["stdout"] = subprocess.PIPE
            kwargs["stderr"] = subprocess.PIPE
            kwargs["universal_newlines"] = True

    try:
        return subprocess.run(["sudo", *args], check=check, **kwargs)
    except subprocess.CalledProcessError as e:
        sys.exit(e.stderr)
