#!/usr/bin/env python

import argparse
from PubPolishPy.parsers import *


def cli_migrate():
    parser = argparse.ArgumentParser(description='Migrate a LaTeX project to a specific format')
    parser.add_argument('src', help="Tex souce file", type=str)
    parser.add_argument("--target", help="Migrate to a submission format", default="generic")
    parser.add_argument("--dest", help="destination folder", default="outPubPolish")

    args = parser.parse_args()

    MAP = {
            'generic': TeXProjectFormatter,
            'ApJ': TeXApJFormatter
            }

    formated = MAP[args.target](args.src, basePath=args.dest) 
    formated.migrate()






