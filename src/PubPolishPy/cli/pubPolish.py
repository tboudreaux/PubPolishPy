#!/usr/bin/env python

import argparse
from PubPolishPy.parsers import *


def cli_migrate():
    parser = argparse.ArgumentParser(description='Migrate a LaTeX project to a specific format help')
    parser.add_argument('src', help="Tex souce file", type=str)
    parser.add_argument("--target", help="Migrate to a submission format", default="generic")
    parser.add_argument("--dest", help="destination folder", default="outPubPolish")
    parser.add_argument("--dry", help="dry run", action="store_true")

    args = parser.parse_args()

    MAP = {
            'Generic': TeXGenericFormatter,
            'ApJ': TeXApJFormatter,
            'ArXiv': TeXArXivFormatter,
            }

    print("Migrating {} to {} format".format(args.src, args.target))
    if args.dry:
        print("Dry run, no files will be written")
    formated = MAP[args.target](args.src, basePath=args.dest) 
    if not args.dry:
        formated.migrate()






