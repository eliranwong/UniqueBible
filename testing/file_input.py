#!/usr/bin/env python

import argparse, sys

parser = argparse.ArgumentParser()
parser.add_argument('filename', nargs='?')
args = parser.parse_args()
if args.filename:
    string = open(args.filename).read()
    print(string)
elif not sys.stdin.isatty():
    string = sys.stdin.read()
    print(string)
else:
    parser.print_help()
