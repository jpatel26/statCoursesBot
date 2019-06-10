#!/usr/bin/env python3
import nltk
import pandas as pd
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize


def penn2morphy(penntag, returnNone=False):
    morphy_tag = {'NN': wn.NOUN, 'JJ': wn.ADJ,
                  'VB': wn.VERB, 'RB': wn.ADV}
    try:
        return morphy_tag[penntag]
    except:
        return None if returnNone else ''


def generate_from_variations(wn, list, current=''):
    if len(wn) == 0:
        list.append(current)
        return
    for variation in wn[0]:
        generate_from_variations(wn[1:], list, current=current + " " + variation)


df = pd.DataFrame.from_csv("questions.tsv", header=1, sep='\t')
generated = []
for i, row in df.head(10).iterrows():
    question = row[0]
    words = word_tokenize(question)
    pos = nltk.pos_tag(words)
    word_syns = []
    i = 0
    skipping = False
    for i in range(len(words)):
        w = words[i]
        if skipping:
            if w == ']':
                skipping = False
            word_syns.append([w])
            continue
        elif w == '[':
            skipping = True
            word_syns.append([w])
            continue

        morphy = penn2morphy(pos[i][1], returnNone=True)
        if morphy is not None:
            syns = set([syn.name().split(".")[0]
                        for syn in wn.synsets(w, morphy)])
        else:
            syns = []

        if len(syns) == 0:
            word_syns.append(set([w]))
        else:
            word_syns.append(syns)
    new = []
    generate_from_variations(word_syns, new)
    print("Original:", question)
    [print(v) for v in new]

    # dfg.to_sql()
