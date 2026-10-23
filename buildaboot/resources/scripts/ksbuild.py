#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

SCRIPT_DIR = Path(__file__).resolve().parent

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("outfile", type=str, help="Output file path")
    parser.add_argument("-j", "--json-input", type=str, metavar="json_file", help="Json input file path")
    parser.add_argument("-s", "--stig", action="store_true", help="Use defaults with additional STIG inputs")

    return parser.parse_args()

def build_kickstart(args):
    if args.stig:
        json_default_file = f"{SCRIPT_DIR}/json/hardening-kickstart-defaults.json"
    else:
        json_default_file = f"{SCRIPT_DIR}/json/kickstart-defaults.json"

    with open(json_default_file, "r") as f:
        ks_defaults = json.load(f)

    if args.json_input:
        with open(args.json_input, "r") as f:
            ks_inputs = json.load(f)

        ksdata = {}
        for k, v in ks_defaults.items():
            if k in ks_inputs:
                ksdata[k] = ks_inputs[k]
            else:
                ksdata[k] = v
        return ksdata
    else:
        return ks_defaults
            
def render_kickstart(ksdata: dict, outfile: str):
    if not isinstance(ksdata, dict):
        print(f"Kickstart data is not a dictionary. ksdata type={type(ksdata)}")
        print(ksdata)
        raise ValueError

    env = Environment(
        loader=FileSystemLoader(f"{SCRIPT_DIR}/templates"),
        undefined=StrictUndefined,
        keep_trailing_newline=True
    )

    template = env.get_template("kickstart.ks.j2")
    
    rendered_kickstart = template.render(**ksdata)

    with open(outfile, "w") as f:
        f.write(rendered_kickstart)

if __name__ == '__main__':
    args = build_parser()
    ksdata = build_kickstart(args)

    render_kickstart(ksdata, args.outfile)

