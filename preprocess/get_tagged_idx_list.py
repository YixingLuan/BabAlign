#!/usr/bin/env python
#-*- coding: utf-8 -*-

import codecs
from collections import defaultdict
import re
import subprocess
import sys
import csv
import argparse

def load_tagged_source(source):

    csv.field_size_limit(sys.maxsize)

    tagged = open(source, "r", encoding="utf-8")
    tagged_tsv = csv.reader(tagged, delimiter="\t")

    id_list = ".".join(source.split(".")[:-1]) + ".tag_idx_list.txt"

    id_f = codecs.open(id_list, "w", encoding="utf-8")

    line_id = 0
    tok_id = 0
    for triple in tagged_tsv:
        lemma = triple[0]
        pos = triple[1]
        i_id = triple[2]
        if lemma == "<eos>":
            line_id += 1
            tok_id = 0
        else:
            if i_id == "x":
                tok_id += 1
                continue
            else:
                line = str(line_id) + "\t" + str(tok_id) + "\t" + i_id + "\t" + lemma + "\n"
                id_f.write(line)
                tok_id += 1

    id_f.close()


def main():

    parser = argparse.ArgumentParser(description='get list of token ids for the tagged focus words')

    parser.add_argument("-s", "--source", default="", help="tsv file for lemmatized tagged source side of the text with pos ({n, v, a, r, x} notations)") 

    args = parser.parse_args()

    load_tagged_source(args.source)


if __name__ == "__main__":
    main()