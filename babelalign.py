#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
1. extract word alignment information from fast_align output
2. extract all possible lexicons from BabelNet output
3. determine final alignment based on following rules:
   - If fast_align alignment exists:
     - If aligned translation is a content word:
       - If aligned translation is in BabelNet lexicons --> keep it 
       - If aligned transaltion is not in BabelNet lexicons --> recover it by using BabelNet lexicon match
     -If aligned translation is a function word --> recover it by using BabelNet lexicon match
   -If fast_align alignment doesn't exist --> recover it by using BabelNet lexicon match
4. If couldn't find proper alignment after step 3, keep using the original alignment or return empty
'''

import codecs
from collections import defaultdict
import re
import sys
import argparse


def load_aligner_output(a_line):

    # assume one-to-one alignment from the base-aligner
    # missed many-to-many alignment can be recovered through complete_match

    align_idx_line = {}
    a_line = a_line.rstrip("\n")
    if a_line == "":
        return align_idx_line

    else:
        a_line_idxs = a_line.split(" ")
        for a_line_idx in a_line_idxs:
            source_idx = a_line_idx.split("-")[0]
            target_idx = a_line_idx.split("-")[1]
            # if multiple target idx exist (many-to-many), choose the most lest one
            align_idx_line.setdefault(source_idx, target_idx)

        return align_idx_line


def load_babelnet_lexicons(f_name, lang1, lang2):

    with codecs.open(f_name, "r", encoding="utf-8") as f:
        babelex_lines = f.readlines()

    src_tgt_babelex = defaultdict(set)
    for line in babelex_lines:
        line = line.rstrip("\n")
        i_id = line.split("\t")[0]
        sense = line.split("\t")[1]

        all_possible_lex = line.split("\t")[2:]
        src_possible_lex = []
        tgt_possible_lex = []
        for possible_lex in all_possible_lex:
            if possible_lex.split(":")[0] == lang1:
                src_possible_lex = possible_lex
            elif possible_lex.split(":")[0] == lang2:
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


def load_target_pos_info(l_p_line, tgt_tok_list):

    tgt_lemma_pos_info = {}
    pos_tokens = l_p_line.rstrip("\n").split(" ")
    for tok_id, (lemma, pos) in enumerate(zip(tgt_tok_list, pos_tokens)):
        tgt_lemma_pos_info[str(tok_id)] = [lemma, pos]

    return tgt_lemma_pos_info


def load_tagged_src_idx(f_name):

    # assume perfect tokenization in src side --> src word is always 1 token (compounds are combined by "_")

    with codecs.open(f_name, "r", encoding="utf-8") as tagf:
        tag_lines = tagf.readlines()

    tag_id_info = defaultdict(dict)
    for count, tag_l in enumerate(tag_lines):
        tag_l = tag_l.rstrip("\n")
        line_id = tag_l.split("\t")[0]
        idx = tag_l.split("\t")[1]
        tag = tag_l.split("\t")[2]
        tag_id_info[line_id][tag] = idx

    return tag_id_info


def complete_match(tgt_idx, target_word, tgt_tok_list, lemma_pos_dict, babel_translations, properly_aligned_ids):

    ori_target_word = target_word # store the original target word
    new_tgt_idx_list = []
    phrase_flag = 0

    previous_tokens_reverse = []
    prev_tgt_idx_list_reverse = []
    #check previous tokens --> only keep proper tokens not violating 2 rules
    # 1. the token is not a function word
    # 2. the token is not properly aligned to other source tokens by aligner
    for i, target_word in enumerate(tgt_tok_list[:int(tgt_idx)][::-1]): 
        if str(int(tgt_idx)-i-1) in properly_aligned_ids or lemma_pos_dict[str(int(tgt_idx)-i-1)][1] == "x":
            break
        else:
            previous_tokens_reverse.append(target_word)
            prev_tgt_idx_list_reverse.append(str(int(tgt_idx)-i-1))
    previous_tokens = previous_tokens_reverse[::-1]
    previous_tgt_idx_list = prev_tgt_idx_list_reverse[::-1]

    following_tokens = []
    following_tgt_idx_list = []
    #check following tokens --> only keep proper tokens not violating 2 rules
    for i, target_word in enumerate(tgt_tok_list[int(tgt_idx)+1:]): 
        if str(int(tgt_idx)+i+1) in properly_aligned_ids or lemma_pos_dict[str(int(tgt_idx)+i+1)][1] == "x":
            break
        else:
            following_tokens.append(target_word)
            following_tgt_idx_list.append(str(int(tgt_idx)+i+1))

    # sort the babel_translations to ensure the longest lexicon
    babel_translations_list = list(babel_translations)
    babel_translations_list.sort(key=lambda x : len(x), reverse=True)

    # if any tokens are valid based on 2 rules --> check if can find the complete phrase
    if previous_tokens != [] or following_tokens != []: 
        tmp_tgt_phrase = "_".join(previous_tokens + [ori_target_word] + following_tokens)
        for babel_t in babel_translations_list:
            if babel_t in tmp_tgt_phrase and ori_target_word in babel_t and babel_t != ori_target_word:
                prev_babel = babel_t.split(ori_target_word)[0]
                follow_babel = babel_t.split(ori_target_word)[1]

                prev_str = ""
                prev_flag = 0
                for pre_idx, pre in zip(prev_tgt_idx_list_reverse, previous_tokens_reverse):
                    prev_str = pre + "_" + prev_str
                    prev_str = prev_str.lstrip("_")
                    if prev_str in prev_babel:
                        new_tgt_idx_list.append(pre_idx)
                        prev_flag += 1
                    else:
                        break
                                        
                follow_str = ""
                follow_flag = 0
                for follow_idx, follow in zip(following_tgt_idx_list, following_tokens):
                    follow_str += follow + "_"
                    follow_str = follow_str.rstrip("_")
                    if follow_str in follow_babel:
                        new_tgt_idx_list.append(follow_idx)
                        follow_flag += 1
                    else:
                        break

                if prev_flag != 0 or follow_flag != 0:
                    target_word = babel_t
                    phrase_flag += 1
                    break

    new_tgt_idx_list.sort(key=lambda x : int(x))

    if phrase_flag != 0:
        return target_word, new_tgt_idx_list

    else:
        return ori_target_word, new_tgt_idx_list


def Babelex_backoff(target_word, tgt_tok_list, lemma_pos_dict, babel_translations, properly_aligned_ids):

    break_flag = 0
    new_tgt_idx_list = []
    new_target_word = target_word
    for t_idx, target_word in enumerate(tgt_tok_list):
        if str(t_idx) in properly_aligned_ids:
            continue
        if lemma_pos_dict[str(t_idx)][1] == "x":
            continue
        if target_word in babel_translations:
            new_tgt_idx_list.append(str(t_idx))
            break_flag += 1
            break

    if break_flag != 0: # if could find 1 token babelex --> try phrase check as well
        new_target_word, new_tgt_idx_list_comp = complete_match(t_idx, target_word, tgt_tok_list, lemma_pos_dict, babel_translations, properly_aligned_ids)
        for new_tgt_idx in new_tgt_idx_list_comp:
            new_tgt_idx_list.append(new_tgt_idx)

    else: # if cannot find babelex --> try it with partial matching
        for t_idx, target_word in enumerate(tgt_tok_list):
            if str(t_idx) in properly_aligned_ids:
                continue
            if lemma_pos_dict[str(t_idx)][1] == "x":
                continue
            phrase_flag = 0
            for babel_t in babel_translations:
                if target_word in babel_t:
                    tmp_target_word, new_tgt_idx_list_comp = complete_match(t_idx, target_word, tgt_tok_list, lemma_pos_dict, babel_translations, properly_aligned_ids)
                    if tmp_target_word != target_word: # properly recovered phrase
                        new_target_word = tmp_target_word
                        for new_tgt_idx in new_tgt_idx_list_comp:
                            new_tgt_idx_list.append(new_tgt_idx)
                        new_tgt_idx_list.append(str(t_idx))
                        phrase_flag += 1
                        break
            if phrase_flag != 0:
                break

    new_tgt_idx_list.sort(key=lambda x : int(x))

    return new_target_word, new_tgt_idx_list


def Babelex_backoff_no_complete(target_word, tgt_tok_list, lemma_pos_dict, babel_translations, properly_aligned_ids):

    new_tgt_idx = ""
    new_target_word = target_word
    for t_idx, target_word in enumerate(tgt_tok_list):
        if str(t_idx) in properly_aligned_ids:
            continue
        if lemma_pos_dict[str(t_idx)][1] == "x":
            continue
        if target_word in babel_translations:
            new_tgt_idx = str(t_idx)
            break

    return new_target_word, new_tgt_idx


def get_properly_aligned_ids(src_tok_list, tgt_tok_list, align_idx_line, src_tgt_babelex, tgt_lemma_pos_info, tag_id_dict):

    properly_aligned_ids = set()

    for tag, src_idx in tag_id_dict.items():

        if src_idx in align_idx_line:
            tgt_idx = align_idx_line[src_idx]
            source_word = src_tok_list[int(src_idx)]
            target_word = tgt_tok_list[int(tgt_idx)]

            # source word is not covered in BabelNet --> cannot do anything
            if source_word not in src_tgt_babelex:
                properly_aligned_ids.add(tgt_idx)
                continue

            # if source word exists in BabelNet --> check BN translations
            babel_translations = src_tgt_babelex[source_word]
            lemma_pos = tgt_lemma_pos_info[tgt_idx]
            if tgt_tok_list[int(tgt_idx)] != lemma_pos[0]: # make sure referring the proper pos info
                print("pos match error:", tag, source_word, target_word, lemma_pos)
                properly_aligned_ids.add(tgt_idx)
                continue

            pos = lemma_pos[1]
            # aligned translation is content word (noun, verb, adjective, adverb) + aligned translation is in possible BN translations
            if pos != "x" and target_word in babel_translations: 
                properly_aligned_ids.add(tgt_idx)

    return properly_aligned_ids 


def finalize_alignment(src_tok_list, tgt_tok_list, align_idx_line, src_tgt_babelex, tgt_lemma_pos_info, tag_id_dict, properly_aligned_ids):

    result_lines = []

    for tag, src_idx in tag_id_dict.items():

        if src_idx in align_idx_line: # if find base aligner alignment --> validity check --> if OK = complete_match, if not = back-off
            source_word = src_tok_list[int(src_idx)]
            tgt_idx = align_idx_line[src_idx]
            target_word = tgt_tok_list[int(tgt_idx)]

            if source_word not in src_tgt_babelex:
                result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                properly_aligned_ids.add(tgt_idx)
                result_lines.append(result_line)
                continue

            babel_translations = src_tgt_babelex[source_word]
            pos_error_flag = 0
            content_flag = 0
            
            lemma_pos = tgt_lemma_pos_info[tgt_idx]
            if tgt_tok_list[int(tgt_idx)] != lemma_pos[0]: # make sure referring the proper pos info
                print("pos match error:", tag, source_word, target_word, lemma_pos)
                result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                properly_aligned_ids.add(tgt_idx)
                result_lines.append(result_line)
                continue

            pos = lemma_pos[1]
            if pos != "x":
                if target_word in babel_translations: # validity check --> OK
                    result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                    properly_aligned_ids.add(tgt_idx)
                    # check multiple-token phrase as well --> we prefer complete matching
                    # (e.g. "orange"="オレンジ　色" both "オレンジ" and "オレンジ色" in BabelNet, but "オレンジ色" is more precise)
                    # rule 1: if the surrounding token is aligned to other src token --> don't combine
                    # rule 2: if the surrounding token is a function word (by pos info) --> don't combine
                    target_word, new_tgt_idx_list = complete_match(tgt_idx, target_word, tgt_tok_list, tgt_lemma_pos_info, babel_translations, properly_aligned_ids)
                    for new_tgt_idx in new_tgt_idx_list:
                        properly_aligned_ids.add(new_tgt_idx)
                    if new_tgt_idx_list != []:
                        result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + ",".join(list(map(str, new_tgt_idx_list))) + "\n"
                    else:
                        result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                else: # if aligned translation is not in babelex --> try to find babelex in the sentence (babelex_backoff)
                    target_word, new_tgt_idx_list = Babelex_backoff(target_word, tgt_tok_list, tgt_lemma_pos_info, babel_translations, properly_aligned_ids)
                    for new_tgt_idx in new_tgt_idx_list:
                        properly_aligned_ids.add(new_tgt_idx)
                    if new_tgt_idx_list != []:
                        result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + ",".join(list(map(str, new_tgt_idx_list))) + "\n"
                    else:
                        result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"

            elif pos == "x": # wrongly aligned to function words --> try to find babelex in the sentence (babelex_backoff)
                target_word, new_tgt_idx_list = Babelex_backoff(target_word, tgt_tok_list, tgt_lemma_pos_info, babel_translations, properly_aligned_ids)
                for new_tgt_idx in new_tgt_idx_list:
                    properly_aligned_ids.add(new_tgt_idx)
                if new_tgt_idx_list != []:
                    result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + ",".join(list(map(str, new_tgt_idx_list))) + "\n"
                else:
                    result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"


        elif src_idx not in align_idx_line: # if no base aligner alignment --> try to find babelex in the sentence (no overlap)
            source_word = src_tok_list[int(src_idx)]
            target_word = None
            if source_word not in src_tgt_babelex: # couldn't find any alignment with BN info
                result_line = tag + "\t" + source_word + "\t" + "NONE" + "\n"
                result_lines.append(result_line)
                continue
            babel_translations = src_tgt_babelex[source_word]
            target_word, new_tgt_idx_list = Babelex_backoff(target_word, tgt_tok_list, tgt_lemma_pos_info, babel_translations, properly_aligned_ids)
            for new_tgt_idx in new_tgt_idx_list:
                properly_aligned_ids.add(new_tgt_idx)
            if new_tgt_idx_list != []:
                result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + ",".join(list(map(str, new_tgt_idx_list))) + "\n"
            else:
                result_line = tag + "\t" + source_word + "\t" + "NONE" + "\n"
            
        result_lines.append(result_line)

    
    return result_lines


def finalize_alignment_no_complete(src_tok_list, tgt_tok_list, align_idx_line, src_tgt_babelex, tgt_lemma_pos_info, tag_id_dict, properly_aligned_ids):

    result_lines = []

    for tag, src_idx in tag_id_dict.items():

        if src_idx in align_idx_line: # if find base aligner alignment --> validity check --> if OK = complete_match, if not = back-off
            source_word = src_tok_list[int(src_idx)]
            tgt_idx = align_idx_line[src_idx]
            target_word = tgt_tok_list[int(tgt_idx)]

            if source_word not in src_tgt_babelex:
                result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                properly_aligned_ids.add(tgt_idx)
                result_lines.append(result_line)
                continue

            babel_translations = src_tgt_babelex[source_word]
            pos_error_flag = 0
            content_flag = 0
            
            lemma_pos = tgt_lemma_pos_info[tgt_idx]
            if tgt_tok_list[int(tgt_idx)] != lemma_pos[0]: # make sure referring the proper pos info
                print("pos match error:", tag, source_word, target_word, lemma_pos)
                result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                properly_aligned_ids.add(tgt_idx)
                result_lines.append(result_line)
                continue

            pos = lemma_pos[1]
            if pos != "x":
                if target_word in babel_translations: # validity check --> OK
                    # since tokenization is perfect --> don't run complete_match
                    result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                    properly_aligned_ids.add(tgt_idx)
                else: # if aligned translation is not in babelex --> try to find babelex in the sentence (babelex_backoff)
                    target_word, new_tgt_idx = Babelex_backoff_no_complete(target_word, tgt_tok_list, tgt_lemma_pos_info, babel_translations, properly_aligned_ids)
                    if new_tgt_idx == "":
                        result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                    else:
                        result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + new_tgt_idx + "\n"

            elif pos == "x": # wrongly aligned to function words --> try to find babelex in the sentence (babelex_backoff)
                target_word, new_tgt_idx = Babelex_backoff_no_complete(target_word, tgt_tok_list, tgt_lemma_pos_info, babel_translations, properly_aligned_ids)
                if new_tgt_idx == "":
                    result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + tgt_idx + "\n"
                else:
                    result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + new_tgt_idx + "\n"


        elif src_idx not in align_idx_line: # if no base aligner alignment --> try to find babelex in the sentence (no overlap)
            source_word = src_tok_list[int(src_idx)]
            target_word = None
            if source_word not in src_tgt_babelex: # couldn't find any alignment with BN info
                result_line = tag + "\t" + source_word + "\t" + "NONE" + "\n"
                result_lines.append(result_line)
                continue
            babel_translations = src_tgt_babelex[source_word]
            target_word, new_tgt_idx = Babelex_backoff_no_complete(target_word, tgt_tok_list, tgt_lemma_pos_info, babel_translations, properly_aligned_ids)
            if target_word:
                result_line = tag + "\t" + source_word + "\t" + target_word + "\t" + src_idx + "-" + new_tgt_idx + "\n"
            else:
                result_line = tag + "\t" + source_word + "\t" + "NONE" + "\n"
            
        result_lines.append(result_line)

    
    return result_lines


def main():

    parser = argparse.ArgumentParser(description='improve alignment accuracy by BabelAlign.')

    parser.add_argument("-s", "--source", default="", help="source side of the text") 
    parser.add_argument("-t", "--target", default="", help="target side of the text")
    parser.add_argument("--idx", default="", help="index list of the source focus word (e.g. output of get_tagged_idx_list.py script)")

    parser.add_argument("-a", "--alignment", default="", help="output from word aligner")

    parser.add_argument("-b", "--babelex", default="", help="BabelNet lexicons file")
    parser.add_argument("-p", "--pos", default="", help="pos file for the target side")

    parser.add_argument("--l1", default="", help="language code of the source side")
    parser.add_argument("--l2", default="", help="language code of the target side")

    parser.add_argument("-o", "--output", default="", help="name of the output file")

    parser.add_argument("--stop_complete", default=False, action="store_true", help="flag to disable complete match for recovering compounds (default: False)")

    args = parser.parse_args() 

    # read line by line to avoid OOM error when using large test bitext
    srcf = codecs.open(args.source, "r", encoding="utf-8")
    src_lem_line = srcf.readline()

    tgtf = codecs.open(args.target, "r", encoding="utf-8")
    tgt_lem_line = tgtf.readline()

    alignf = codecs.open(args.alignment, "r", encoding="utf-8")
    align_line = alignf.readline()

    posf = codecs.open(args.pos, "r", encoding="utf-8")
    tgt_pos_line = posf.readline()

    src_tgt_babelex = load_babelnet_lexicons(args.babelex, args.l1, args.l2)
    tag_id_info = load_tagged_src_idx(args.idx)

    newf = codecs.open(args.output, "w", encoding="utf-8")


    if args.stop_complete:

        line_id = 0
        while src_lem_line:

            if line_id % 500000 == 0:
                print("processed", line_id, "lines")


            src_tokens = src_lem_line.rstrip("\n").lower().split(" ")
            tgt_tokens = tgt_lem_line.rstrip("\n").lower().split(" ")
            align_idx_line = load_aligner_output(align_line)

            if line_id > len(tag_id_info):
                break

            tag_ids = tag_id_info[str(line_id)]

            tgt_lemma_pos_info = load_target_pos_info(tgt_pos_line, tgt_tokens)

            properly_aligned_ids = get_properly_aligned_ids(src_tokens, tgt_tokens, align_idx_line, src_tgt_babelex, tgt_lemma_pos_info, tag_ids)
            result_lines = finalize_alignment_no_complete(src_tokens, tgt_tokens, align_idx_line, src_tgt_babelex, tgt_lemma_pos_info, tag_ids, properly_aligned_ids)

            for result_line in result_lines:
                newf.write(result_line)

            src_lem_line = srcf.readline()
            tgt_lem_line = tgtf.readline()
            align_line = alignf.readline()
            tgt_pos_line = posf.readline()
            line_id += 1

    
    else:

        line_id = 0
        while src_lem_line:

            if line_id % 500000 == 0:
                print("processed", line_id, "lines")


            src_tokens = src_lem_line.rstrip("\n").lower().split(" ")
            tgt_tokens = tgt_lem_line.rstrip("\n").lower().split(" ")
            align_idx_line = load_aligner_output(align_line)

            if line_id > len(tag_id_info):
                break

            tag_ids = tag_id_info[str(line_id)]

            tgt_lemma_pos_info = load_target_pos_info(tgt_pos_line, tgt_tokens)

            properly_aligned_ids = get_properly_aligned_ids(src_tokens, tgt_tokens, align_idx_line, src_tgt_babelex, tgt_lemma_pos_info, tag_ids)
            result_lines = finalize_alignment(src_tokens, tgt_tokens, align_idx_line, src_tgt_babelex, tgt_lemma_pos_info, tag_ids, properly_aligned_ids)

            for result_line in result_lines:
                newf.write(result_line)

            src_lem_line = srcf.readline()
            tgt_lem_line = tgtf.readline()
            align_line = alignf.readline()
            tgt_pos_line = posf.readline()
            line_id += 1


    srcf.close()
    tgtf.close()
    alignf.close()
    posf.close()

    newf.close()


if __name__ == "__main__":
    main()

