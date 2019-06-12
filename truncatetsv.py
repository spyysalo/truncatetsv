#!/usr/bin/env python3

import sys
import os


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('-c', '--skip-comments', default=False, action='store_true',
                    help='do not truncate lines starting with "#"')
    ap.add_argument('-f', '--fields', metavar='INT[,...]',
                    help='TSV fields to truncate (default: all)')
    ap.add_argument('-l', '--length', metavar='INT', type=int, required=True,
                    help='length to truncate to')
    ap.add_argument('file', metavar='TSV', nargs='+',
                    help='TSV files')
    return ap


def main(argv):
    args = argparser().parse_args(argv[1:])
    if args.fields is not None:
        args.fields = [int(i) for i in args.fields.split(',')]
    for fn in args.file:
        with open(fn) as f:
            for ln, l in enumerate(f, start=1):
                l = l.rstrip('\n')
                if l == '' or l.isspace():
                    print(l)
                    continue
                if args.skip_comments and l.startswith('#'):
                    print(l)
                    continue
                fields = l.split('\t')
                if args.fields is None:
                    fields = [f[:args.length] for f in fields]
                else:
                    for f in args.fields:
                        fields[f] = fields[f][:args.length]
                print('\t'.join(fields))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
