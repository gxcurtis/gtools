#!/usr/bin/env python3
import json
import argparse
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=str, help="Path to json file for input")
    parser.add_argument("-o", "--output", type=str, default="build-product.ks", help="Set output path of kickstart")

    return parser.parse_args()

def build_kickstart(json_input_file, json_default_file="json/kickstart-defaults.json"):

    with open(json_input_file, "r") as f:
        ks_inputs = json.load(f)
    
    with open(json_default_file, "r") as f:
        ks_defaults = json.load(f)

    ksdata = {}
    for k, v in ks_defaults.items():
        if k in ks_inputs:
            ksdata[k] = ks_inputs[k]
        else:
            ksdata[k] = v
    return ksdata
            
def render_kickstart(ksdata: dict, output_file: str):
    if not isinstance(ksdata, dict):
        print(f"Kickstart data is not a dictionary. ksdata type={type(ksdata)}")
        print(ksdata)
        raise ValueError

    env = Environment(
        loader=FileSystemLoader("templates"),
        undefined=StrictUndefined,
        keep_trailing_newline=True
    )

    template = env.get_template("kickstart.ks.j2")
    
    rendered_kickstart = template.render(**ksdata)

    with open(output_file, "w") as f:
        f.write(rendered_kickstart)

if __name__ == '__main__':
    args = build_parser()
    ksdata = build_kickstart(args.json_file)

    render_kickstart(ksdata, args.output)

