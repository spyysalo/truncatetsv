#!/usr/bin/env python3

# Variant of the `paste` command for modifying CoNLL-U data

import sys
import os

from collections.abc import Iterator
from itertools import tee


CONLLU_FIELDS = [
    'ID',
    'FORM',
    'LEMMA',
    'UPOS',
    'XPOS',
    'FEATS',
    'HEAD',
    'DEPREL',
    'DEPS',
    'MISC',
]


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('-f', '--field', metavar='INT', default=5, type=int,
                    help='index of CoNLL-U field to paste to')
    ap.add_argument('-s', '--separator', default='-',
                    help='string separating pasted from existing value')
    ap.add_argument('-t', '--text-field', metavar='INT', default=1, type=int,
                    help='index of TSV field with token text')
    ap.add_argument('conllu')
    ap.add_argument('tsv')
    return ap


class FormatError(Exception):
    pass


class LookaheadIterator(Iterator):
    """Lookahead iterator from http://stackoverflow.com/a/1518097."""

    def __init__(self, it, start=0):
        self._it, self._nextit = tee(iter(it))
        self.index = start - 1
        self._advance()

    def _advance(self):
        self.lookahead = next(self._nextit, None)
        self.index = self.index + 1

    def __next__(self):
        self._advance()
        return next(self._it)

    def __bool__(self):
        return self.lookahead is not None


def process(conllu, tsv, options, out=None):
    if out is None:
        out = sys.stdout
    form_idx = CONLLU_FIELDS.index('FORM')
    conllu = LookaheadIterator(conllu)
    tsv = LookaheadIterator(tsv)
    while conllu and tsv:
        if conllu.lookahead.isspace() or conllu.lookahead.startswith('#'):
            out.write(conllu.lookahead)
            next(conllu)
        elif not tsv.lookahead or tsv.lookahead.isspace():
            next(tsv)
        else:
            c_fields = conllu.lookahead.rstrip('\n').split('\t')
            if len(c_fields) != len(CONLLU_FIELDS):
                raise FormatError('expected 10 tab-separated fields, got {}'.\
                                  format(len(c_fields)))            
            t_fields = tsv.lookahead.rstrip('\n').split('\t')
            if len(t_fields) != 2:
                raise FormatError('expected two tab-separated fields, for {}'.\
                                  format(len(t_fields)))
            c_form = c_fields[form_idx]
            t_form = t_fields[options.text_field-1]    # 1-based
            if c_form != t_form:
                raise ValueError('form mismatch: "{}" != "{}"'.format(
                    c_form, t_form))
            t_value = t_fields[1-(options.text_field-1)]    # the other one
            c_fields[options.field-1] += options.separator + t_value
            out.write('\t'.join(c_fields)+'\n')
            next(conllu)
            next(tsv)


def main(argv):
    args = argparser().parse_args(argv[1:])
    with open(args.conllu) as conllu:
        with open(args.tsv) as tsv:
            process(conllu, tsv, args)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
