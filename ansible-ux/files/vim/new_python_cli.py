#!/usr/bin/env python3
import argparse
import subprocess
import sys

# Python CLI class interface
class CLI:
    
    @staticmethod
    def run(*args, capture=True, check=True, **kwargs):
        if capture:
            if sys.version_info >= (3,8):
                kwargs["capture_output"] = True
                kwargs["text"] = True
            else:
                kwargs["stdout"] = subprocess.PIPE
                kwargs["stderr"] = subprocess.PIPE
                kwargs["universal_newlines"] = True

        try:
            return subprocess.run([*args], check=check, **kwargs)
        except subprocess.CalledProcessError as e:
            sys.exit(e.stderr)
    
    @staticmethod
    def parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()

        return parser

def main():
    parser = CLI.parser()
    
    args = parser.parse_args()

# Run main
if __name__ == "__main__":
    sys.exit(main())
