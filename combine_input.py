#!/usr/bin/env python
#-*- coding: utf-8 -*-

import codecs
import re
import regex
import unicodedata
from collections import defaultdict
import sys
import argparse

"""
Combine
- sentence align + combine by " ||| " for fast_align input
- if a sentence should be removed in one side, corresponding sentence in the other side should be also removed.
  (to maintain sentence alignment)

"""


def load_src(f_name):

    with codecs.open(f_name, "r", encoding="utf-8") as f:
        f_lines = f.readlines()

    src_lines = []
    for l in f_lines:
        l = l.rstrip("\n")
        l = l.rstrip("\r")
        src_lines.append(l.lower())

    return src_lines


def load_tgt(f_name):

    with codecs.open(f_name, "r", encoding="utf-8") as f:
        f_lines = f.readlines()

    tgt_lines = []
    for l in f_lines:
        l = l.rstrip("\n")
        l = l.rstrip("\r")
        tgt_lines.append(l.lower())

    return tgt_lines


def load_babelnet_lexicons(f_name, lang1, lang2):

    with codecs.open(f_name, "r", encoding="utf-8") as f:
        babelex_lines = f.readlines()

    src_tgt_babelex = defaultdict(set)
    for line in babelex_lines:
        line = line.rstrip("\n")
        sense = line.split("\t")[0]

        all_possible_lex = line.split("\t")[1:]
        src_possible_lex = []
        tgt_possible_lex = []
        for possible_lex in all_possible_lex:
            if possible_lex.split(":")[0] == lang1.upper():
                src_possible_lex = possible_lex
            elif possible_lex.split(":")[0] == lang2.upper():
                tgt_possible_lex = possible_lex

        if src_possible_lex == [] or tgt_possible_lex == []:
            continue
        else:
            src_lex_list = src_possible_lex.split(":")[1].split(",")
            tgt_lex_list = tgt_possible_lex.split(":")[1].split(",")
            for src_lex in src_lex_list:
                for tgt_lex in tgt_lex_list:
                    src_tgt_babelex[src_lex].add(tgt_lex)

    return src_tgt_babelex
    

def combine_for_alignment(src_lines, tgt_lines, bitxt_src, bitxt_tgt, src_tgt_babelex, out_name):

    with codecs.open(bitxt_src, "r", encoding="utf-8") as srcf:
        bi_src_lines = srcf.readlines()

    with codecs.open(bitxt_tgt, "r", encoding="utf-8") as tgtf:
        bi_tgt_lines = tgtf.readlines()

    newf = codecs.open(out_name, "w", encoding="utf-8")

    for s_line, t_line in zip(src_lines, tgt_lines):
        s_t_line = s_line + " ||| " + t_line + "\n"
        newf.write(s_t_line)

    empty = ["", " ", "  ", "   ", "    "]
    for s_line, t_line in zip(bi_src_lines, bi_tgt_lines):
        s_line = s_line.rstrip("\n")
        s_line = s_line.rstrip("\r")
        t_line = t_line.rstrip("\n")
        t_line = t_line.rstrip("\r")
        if s_line not in empty and t_line not in empty:
            s_t_line = s_line + " ||| " + t_line + "\n"
        newf.write(s_t_line)

    alpha = re.compile('[a-zA-Z]+')
    kanji = regex.compile(r"\p{Han}+")
    kata = regex.compile(r"\p{Katakana}+")
    hira = regex.compile(r"\p{Hiragana}+")
    for s_lex, t_lex_set in src_tgt_babelex.items():
        if s_lex == "" or s_lex == " ":
            continue
        if alpha.match(s_lex): # need to remove weired symbols from lexicon pairs
            for t_lex in t_lex_set:
                if t_lex == "" or t_lex == " ": # sometimes empty token is included
                    continue
                if alpha.match(t_lex) or kanji.match(t_lex) or kata.match(t_lex) or hira.match(t_lex):
                    s_t_line = s_lex + " ||| " + t_lex + "\n"

                    newf.write(s_t_line)


    newf.close()


def combine_for_alignment_less(src_lines, tgt_lines, src_tgt_babelex, out_name):


    newf = codecs.open(out_name, "w", encoding="utf-8")

    for s_line, t_line in zip(src_lines, tgt_lines):
        s_t_line = s_line + " ||| " + t_line + "\n"
        newf.write(s_t_line)

    alpha = re.compile('[a-zA-Z]+')
    kanji = regex.compile(r"\p{Han}+")
    kata = regex.compile(r"\p{Katakana}+")
    hira = regex.compile(r"\p{Hiragana}+")
    for s_lex, t_lex_set in src_tgt_babelex.items():
        if s_lex == "" or s_lex == " ":
            continue
        if alpha.match(s_lex): # need to remove weired symbols from lexicon pairs
            for t_lex in t_lex_set:
                if t_lex == "" or t_lex == " ": # sometimes empty token is included
                    continue
                if alpha.match(t_lex) or kanji.match(t_lex) or kata.match(t_lex) or hira.match(t_lex):
                    s_t_line = s_lex + " ||| " + t_lex + "\n"

                    newf.write(s_t_line)


    newf.close()


def main():

    parser = argparse.ArgumentParser(description='create the input data for word aligner.')

    parser.add_argument("-s", "--source", default="", help="lemmatized source side of the text") 
    parser.add_argument("-t", "--target", default="", help="lemmatized target side of the text")

    parser.add_argument("--bi1", default="", help="source side of the additional bitext (optional)") 
    parser.add_argument("--bi2", default="", help="target side of the additional bitext (optional)")

    parser.add_argument("-b", "--babelex", default="", help="BabelNet lexicons file")
    parser.add_argument("--l1", default="", help="language code of the source side")
    parser.add_argument("--l2", default="", help="language code of the target side")

    parser.add_argument("-o", "--output", default="", help="name of the created input data for the word aligner")

    args = parser.parse_args()

    src_lines = load_src(args.source)
    tgt_lines = load_tgt(args.target)

    src_tgt_babelex = load_babelnet_lexicons(args.babelex, args.l1, args.l2)

    if args.bi1 != "" and args.bi2 != "":
        combine_for_alignment(src_lines, tgt_lines, args.bi1, args.bi2, src_tgt_babelex, args.output)
    else:
        combine_for_alignment_less(src_lines, tgt_lines, src_tgt_babelex, args.output)



if __name__ == "__main__":
    main()