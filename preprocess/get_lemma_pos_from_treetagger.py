#!/usr/bin/env python
#-*- coding: utf-8 -*-

import codecs
from collections import defaultdict
import subprocess
import sys
import argparse


def process_input_for_treetagger(f_name):
    # use @ as a sentencial marker

    with codecs.open(f_name, "r", encoding="utf-8") as f:
        it_sentences = f.readlines()

    tree_in_name = f_name + ".tree_in"
    tree_out_name = f_name + ".tree_out"

    with codecs.open(tree_in_name, "w", encoding="utf-8") as newf:
        for sent in it_sentences:
            sent = sent.replace("@", "ATMARK")
            newf.write(sent)
            newf.write("@\n") # insert this to indicate each sentence for TreeTagger output processing

    print("preprocess: done")

    return tree_in_name, tree_out_name


def run_treetagger(tree_in_name, tree_out_name, lang):

    if lang.upper() == "EN":
        cmd = "cat " + tree_in_name + " | TreeTagger/cmd/tree-tagger-english > " + tree_out_name

    elif lang.upper() == "IT":
        cmd = "cat " + tree_in_name + " | TreeTagger/cmd/tree-tagger-italian > " + tree_out_name

    elif lang.upper() == "DE":
        cmd = "cat " + tree_in_name + " | TreeTagger/cmd/tree-tagger-german > " + tree_out_name

    elif lang.upper() == "ES":
        cmd = "cat " + tree_in_name + " | TreeTagger/cmd/tree-tagger-spanish > " + tree_out_name

    elif lang.upper() == "FR":
        cmd = "cat " + tree_in_name + " | TreeTagger/cmd/tree-tagger-french > " + tree_out_name

    elif lang.upper() == "RU":
        cmd = "cat " + tree_in_name + " | TreeTagger/cmd/tree-tagger-russian > " + tree_out_name

    #subprocess.run(cmd, shell=True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
    subprocess.run(cmd, shell=True)

    print("run: done")

    rm_cmd = "rm -f " + tree_in_name
    subprocess.run(rm_cmd, shell=True)


def process_treetagger_output(tree_out_name, lang):

    f = codecs.open(tree_out_name, "r", encoding="utf-8")
        
    out = f.readline() # considering the memory issue, use readline() instead of readlines()

    treetagger_outputs = []
    tree_output = []

    # marker to indicate the end of sentence
    if lang.upper() == "EN":
        marker1 = "@\tSYM\t@" # PenTreeBank tagset
        marker2 = "@\tPRP\t@" # BNC tagset
    elif lang.upper() == "IT":
        marker = "@\tSYM\t@"
    elif lang.upper() == "DE":
        marker = "@\tXY\t@"
    elif lang.upper() == "ES":
        marker = "@"
    elif lang.upper() == "FR":
        marker = "@"
    elif lang.upper() == "RU":
        marker = "@\t-\t@"

    if lang.upper() == "EN":
        while out:
            out = out.rstrip("\n")
            if out == marker1 or out == marker2:
                treetagger_outputs.append(tree_output)
                tree_output = []
            else:
                tree_output.append(out)

            out = f.readline()
    
    if lang.upper() in ["IT", "DE", "RU"]:
        while out:
            out = out.rstrip("\n")
            if out == marker:
                treetagger_outputs.append(tree_output)
                tree_output = []
            else:
                tree_output.append(out)

            out = f.readline()

    if lang.upper() in ["ES", "FR"]:
        while out:
            out = out.rstrip("\n")
            if out.split("\t")[0] == marker:
                treetagger_outputs.append(tree_output)
                tree_output = []
            else:
                tree_output.append(out)

            out = f.readline()


    print("read: done")

    tree_out_lemma_sentences = []
    tree_out_pos_sentences = []

    for tree_output_tokens in treetagger_outputs:

        tree_out_lemma_line = ""
        tree_out_pos_line = ""
        for out in tree_output_tokens:
            out = out.rstrip("\n")
            token = out.split("\t")[0]
            raw_pos = out.split("\t")[1]
            lemma = out.split("\t")[2]
            if token == "ATMARK":
                lemma = "@"
            if lemma == "<unknown>" or lemma == "@card@":
                lemma = token
            if token != "ATMARK" and "ATMARK" in token:   
                lemma = lemma.replace("ATMARK", "@")

            if lang.upper() == "EN":
                if raw_pos in ["NN0", "NN1", "NN2", "NP0"]: # noun or name
                    pos = "n"
                elif raw_pos[0] == "V":
                    pos = "v"
                elif raw_pos in ["AJ0, AJC, AJS"]:
                    pos = "a"
                elif raw_pos in ["AV0", "AVP", "AVQ"]:
                    pos = "r"
                else:
                    pos = "x"

            elif lang.upper() == "IT":
                if raw_pos == "NOM" or raw_pos == "NPR": # noun or name 
                    pos = "n"
                elif raw_pos[0] == "V":
                    pos = "v"
                elif raw_pos == "ADJ":
                    pos = "a"
                elif raw_pos == "ADV":
                    pos = "r"
                else:
                    pos = "x"

            elif lang.upper() == "DE":
                if raw_pos == "NN" or raw_pos == "NE": # noun or name 
                    pos = "n"
                elif raw_pos[0] == "V":
                    pos = "v"
                elif raw_pos[:3] == "ADJ":
                    pos = "a"
                elif raw_pos == "ADV":
                    pos = "r"
                else:
                    pos = "x"

            elif lang.upper() == "ES":
                if raw_pos == "NC" or raw_pos == "NP" or raw_pos[:2] == "PP" or raw_pos == "REL": # noun or name
                    pos = "n"
                elif raw_pos[0] == "V":
                    pos = "v"
                elif raw_pos == "ADJ":
                    pos = "a"
                elif raw_pos == "ADV":
                    pos = "r"
                else:
                    pos = "x"

            elif lang.upper() == "FR":
                if raw_pos == "NOM":
                    pos = "n"
                elif raw_pos[0] == "V":
                    pos = "v"
                elif raw_pos == "ADJ":
                    pos = "a"
                elif raw_pos == "ADV":
                    pos = "r"
                else:
                    pos = "x"                

            elif lang.upper() == "RU":
                if raw_pos[0] == "N":
                    pos = "n"
                elif raw_pos[0] == "V":
                    pos = "v"
                elif raw_pos[0] == "A":
                    pos = "a"
                elif raw_pos[0] == "R":
                    pos = "r"
                else:
                    pos = "x"

            if lemma != "|":
                lemma = lemma.split("|")[0]
            if " " in lemma:
                lemma = lemma.replace(" ", "_")
            tree_out_lemma_line += lemma + " "
            tree_out_pos_line += pos + " "

        tree_out_lemma_sentences.append(tree_out_lemma_line.rstrip(" "))
        tree_out_pos_sentences.append(tree_out_pos_line.rstrip(" "))

    print("process: done")

    rm_cmd = "rm -f " + tree_out_name
    subprocess.run(rm_cmd, shell=True)

    return tree_out_lemma_sentences, tree_out_pos_sentences


def main():

    parser = argparse.ArgumentParser(description='run and process treetagger')

    parser.add_argument("-i", "--input", default="", help="input data for treetagger (raw text)") 
    parser.add_argument("-l", "--lang", default="", help="language code of the input data (EN, IT, DE, ES, FR, RU)")

    parser.add_argument("--lem", default="", help="output filename for lemmatized text")
    parser.add_argument("--pos", default="", help="output filename for pos-tagged text")

    args = parser.parse_args() 

    tree_in_name, tree_out_name = process_input_for_treetagger(args.input)
    run_treetagger(tree_in_name, tree_out_name, args.lang)
    tree_out_lemma_sentences, tree_out_pos_sentences = process_treetagger_output(tree_out_name, args.lang)

    newf1 = codecs.open(args.lem, "w", encoding="utf-8")
    newf2 = codecs.open(args.pos, "w", encoding="utf-8")

    for line in tree_out_lemma_sentences:
        newf1.write(line)
        newf1.write("\n")

    for line in tree_out_pos_sentences:
        newf2.write(line)
        newf2.write("\n")

    print("write: done")

    newf1.close()
    newf2.close()


if __name__ == "__main__":
    main()
