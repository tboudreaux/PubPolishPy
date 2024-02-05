#!/usr/bin/env python

import argparse
from PubPolishPy.parsers import *
import shutil


def cli_migrate():
    parser = argparse.ArgumentParser(description='Migrate a LaTeX project to a specific format help')
    parser.add_argument('src', help="Tex souce file", type=str)
    parser.add_argument("--target", help="Migrate to a submission format", default="generic")
    parser.add_argument("--dest", help="destination folder", default="outPubPolish")
    parser.add_argument("--dry", help="dry run", action="store_true")
    parser.add_argument("-f", "--force", help="Migrate even if folder exists", action="store_true", default=False)
    parser.add_argument("--additional", help="Any additional files not in the tex tree to be copied", type=str, nargs="*")

    args = parser.parse_args()

    MAP = {
            'Generic': TeXGenericFormatter,
            'ApJ': TeXApJFormatter,
            'ArXiv': TeXArXivFormatter,
            }

    print("Migrating {} to {} format".format(args.src, args.target))
    if args.dry:
        print("Dry run, no files will be written")

    if args.force:
        print("Forcing migration, destination folder will be overwritten")
        shutil.rmtree(args.dest, ignore_errors=True)
    formated = MAP[args.target](args.src, basePath=args.dest) 
    if not args.dry:
        formated.migrate()

    if args.additional != None:
        for a in args.additional:
            print("Copying additional file {}".format(a))
            if not args.dry:
                shutil.copy(a, args.dest)






