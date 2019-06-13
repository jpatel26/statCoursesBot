#!/usr/bin/env python3
import logging
import random
import re
import string
import warnings
from collections import namedtuple

import nltk
import numpy as np
import pandas as pd
from nltk.stem import PorterStemmer, WordNetLemmatizer

from .answer_quest import answer as ans
from .loader import load_synonym_table, load_questions

warnings.filterwarnings("ignore")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics.classification import accuracy_score
from nltk.corpus import stopwords as _sw

logging.basicConfig(level=logging.INFO)
lemmatizer = nltk.stem.WordNetLemmatizer
stopwords = _sw.words('english')
ps = PorterStemmer()
lm = WordNetLemmatizer()

punct_dict = {ord(punct): None for punct in string.punctuation}
FoundVariable = namedtuple("FoundVariable", "start end content results")
Match = namedtuple("Match", "label similarity")
Synonym = namedtuple('Synonym', 'table column canon')
StaciaMsg = namedtuple('StaciaMsg', 'status content')


def stem_tokens(tokens):
    return [ps.stem(token) for token in tokens]


def lemmatize_tokens(tokens):
    return [lm.lemmatize(token) for token in tokens]


def reduce_tokens(tokens, reducer=stem_tokens):
    return reducer(tokens)


def translated_tokens(text):
    return nltk.word_tokenize(text.lower().translate(punct_dict))


def stem_normalize(text):
    return stem_tokens(translated_tokens(text))


def is_variable(word):
    return word.startswith('[') and word.endswith(']')


def question_stem_normalize(text):
    return stem_tokens(
        [word for word in translated_tokens(text) if not is_variable(word)])


class TfidfClassifier:
    def __init__(self, tokenizer=stem_normalize, stop_words=None, ngram_range=(1, 3), analyzer='word'):
        self.tokenizer = tokenizer
        self.stop_words = stop_words
        self.ngram_range = ngram_range
        self.analyzer = analyzer
        self.tfidf = None
        self.labels = None
        self.label_extractor = None
        self.model = TfidfVectorizer(tokenizer=self.tokenizer,
                                     stop_words=self.stop_words,
                                     ngram_range=self.ngram_range,
                                     analyzer=self.analyzer)

    def fit_transform(self, X, Y, label_extractor=None):
        self.tfidf = self.model.fit_transform(X)
        self.labels = Y
        self.label_extractor = label_extractor

    def train_and_evaluate(self, X, Y, label_extractor=None):
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1)
        self.fit_transform(X_train, Y_train, label_extractor=label_extractor)
        Y_pred = [self.predict(x)[0].canon for x in X_test]
        Y_test = [y.canon for y in Y_test]
        print(accuracy_score(Y_test, Y_pred))

    def predict(self, Y):
        return self.predict_take_all(Y)[0]

    def predict_take_all(self, Y):
        vec = self.model.transform([Y])
        similarity = cosine_similarity(vec, self.tfidf)[0]  # Get similarity to all entries
        # Find max similarity for each label
        label_max = {}
        for id in range(len(similarity)):
            label = self.label_of(id)
            label_max[label] = max(label_max.get(label, 0), similarity[id])

        # Return labels sorted by their highest similarity
        srt = sorted(label_max.items(), key=lambda x: x[1], reverse=True)
        return [Match(entry[0], entry[1]) for entry in srt if entry[1] > 0]

    def label_of(self, index):
        if self.label_extractor is not None:
            return self.label_extractor(self.labels, index)
        return self.labels[index]

    def similarity_of(self, vec, compared_to):
        return cosine_similarity(vec, self.tfidf)[0][compared_to]


def row_extractor(df, idx):
    return df.loc[idx, :]


non_starters = ['statistical', 'teach', 'quarter', 'professor', 'teacher']
non_starters.extend(stopwords)


def variable_scan(classifier, query, is_exclusive=True, is_relevant=(lambda x: True)):
    variables = []
    words = [word.lower() for word in nltk.word_tokenize(query)]
    i = -1
    while i < len(words) - 1:
        i = i + 1
        w = words[i]
        if w in non_starters: continue
        results = classifier.predict_take_all(w)
        if len(results) == 0 or results[0].similarity < 0.3:
            if all([c.isdigit() for c in w]):
                variables.append(
                    FoundVariable(i, i + 1, w,
                                  [Match(Synonym(None, 'number', w), 1.0)]))
            continue
        j = i + 1
        while j < len(words) - 1:
            j = j + 1
            if words[j - 1] in ['.', ',']:
                break
            w = " ".join(words[i:j])
            next = classifier.predict_take_all(w)
            if next[0].similarity > 0.90:
                # End due to certainty
                results = next
                break
            if sum_matching(next) < sum_matching(results):
                # End due to die-off
                break
            results = next
        results = [res for res in results if is_relevant(res)]
        if len(results):
            variables.append(FoundVariable(i, j, w, results))
            # Found something and flag is on
            if is_exclusive:
                i = j - 1
    return variables


def sum_matching(matching):
    return sum([conf for _, conf in matching])


def is_relevant_col(columns, minsim=0.3):
    return lambda row: row[0].column in columns and row[1] > minsim


def meets_minsim(minsim=0.3):
    return lambda row: row[1] > minsim


variable_to_col = {
    '[STAT-COURSE]': 'course_num',
    '[COURSE-LIST]': 'course_num',
    '[TOPIC]': 'course_num',
    '[STAT-FACULTY]': 'faculty_last_name',
    '[ROOM]': 'course_room',
    '[COURSE-NUMBER]': 'course_num',
    '[COURSE-TITLE]': 'course_num',
    '[TERM]': 'term',
    '[COURSE-LEVEL]': 'course_level'
}


def get_query_vars(question):
    return [var for var in variable_to_col if var in question]


def print_extracted(variables, title="Extracted Variables"):
    print(f"----{title}----")
    for fv in variables:
        print("Index:", fv.start)
        print("Content:", fv.content)
        print("Top 3 Results:")
        for res, sim in fv.results[:3]:
            print(res.canon, " -> ", sim)


def question_vars(question):
    vars = re.findall(r"\[(.*?)\]", question)
    return ["[" + var + "]" for var in vars]


syn_table = load_synonym_table()
syn_entries = syn_table['synon']  # Documents
syn_labels = [Synonym(row[1], row[2], row[3]) for row in syn_table.itertuples()]  # Labels

question_df = load_questions()
question_entries = question_df['question']  # Documents
answer_id_labels = question_df['answerId']
answer_labels = question_df['a_primary']

answers = {row.answerId: row.question for row in question_df.itertuples()}
answer_variables = {row.answerId: question_vars(row.question) for row in question_df.itertuples()}

tfSynClassifier = TfidfClassifier(stop_words='english', analyzer='char_wb', ngram_range=(4, 5))
tfSynClassifier.fit_transform(syn_entries, syn_labels)

X, y = question_entries, answer_id_labels
tfQuestionClassifier = TfidfClassifier(tokenizer=question_stem_normalize, analyzer='char', ngram_range=(4, 5))
tfQuestionClassifier.fit_transform(X, y)

mlp = MLPClassifier(max_iter=400)
tfidf_matrix = tfQuestionClassifier.model.transform(X)
df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfQuestionClassifier.model.get_feature_names(), index=y)
new_features = []
for x in X:
    to_add = {}
    to_add['__course_num'] = float(x.count('[STAT-COURSE]') + x.count('[TOPIC]') + x.count('[COURSE-NUMBER]') + x.count(
        '[COURSE-TITLE]') + x.count('[COURSE-LIST]') * 3)
    to_add['__term'] = float(x.count('[TERM]'))
    to_add['__faculty_last_name'] = float(x.count('[STAT-FACULTY]'))
    to_add['__day'] = float(x.count('[DAY]'))
    to_add['__number'] = float(x.count('[NUM_CREDITS]') + x.count('[NUM-RATING]'))
    new_features.append(to_add)
df2 = pd.DataFrame(new_features, index=y)
df = pd.concat([df, df2], axis=1)

mlp.fit(df.values, y)


def classify(query):
    matrix = tfQuestionClassifier.model.transform([query])[0].toarray()
    variables = variable_scan(tfSynClassifier, query, is_relevant=meets_minsim())
    __courses, __terms, __faculty, __days, __numbers = 0, 0, 0, 0, 0
    for var in variables:
        _, _, _, res = var
        label, sim = res[0]
        if label.column == 'course_num':
            __courses += sim
        if label.column == 'term':
            __terms += sim
        if label.column == 'faculty_last_name':
            __faculty += sim
        if label.column == 'course_days':
            __days += sim
        if label.column == 'number':
            __numbers += sim
    full_features = np.append(matrix, [__courses, __terms, __faculty, __days, __numbers])

    mlp_prediction = mlp.predict_proba([full_features])[0]
    best = mlp_prediction.argmax()  # Choose the one with highest confidence
    return mlp.classes_[best], mlp_prediction[best], variables


def find_next(var_name, col_name, variables):
    found = []
    for i in range(len(variables)):
        _, _, _, results = variables[i]
        if results[0].label.column == col_name:
            last_added = None
            for syn, sim in results:
                if syn.column == col_name \
                        and syn.canon not in found:
                    if var_name == "[TOPIC]":
                        found.append(syn.canon)
                    elif last_added is not None:
                        if sim > 0.1 and abs(last_added - sim) < 1e-4:
                            found.append(syn.canon)
                    else:
                        found.append(syn.canon)
                    last_added = sim
            variables.pop(i)
            return found
    return None


def match_to_variables(aid, variables):
    qvars = answer_variables[aid]
    columns = [variable_to_col[var] for var in qvars]
    avars = {var_name: [] for var_name in qvars}
    for var_name, col in zip(qvars, columns):
        if var_name == '[COURSE-LIST]':
            colvars = []
            nxt = find_next(var_name, col, variables)
            while nxt is not None:
                colvars.append(nxt)
                nxt = find_next(var_name, col, variables)
            if len(colvars) == 0:
                return None
            avars[var_name] = colvars
            continue

        nxt = find_next(var_name, col, variables)
        if nxt is None:
            return None
        avars[var_name].append(nxt)
    return avars


greetings = ["Hi! I'm StaCIA. Do you have any questions about Statistics courses?",
             "How can I help?",
             "I'm listening...",
             "StaCIA here. Can I help you with Statistics courses?",
             "Hi, I'm Stacia. What can I help you with?"]
outside_domain = ["Hmm. I don't see anything in your question that fits my domain knowledge.",
                  "I don't think I can properly answer that. I specialize in Statistics courses.",
                  "You might have to ask someone else."]
no_answer = ["I'm don't understand what you are asking...",
             "I don't know.",
             "That question doesn't make sense to me. I'm quite limited, you see..."]
not_enough_info = ["I wasn't able to get enough information out of your question to give a good answer.",
                   "Can you rephrase that? I don't have quite enough information.",
                   "Could I get some more information?"]
goodbye = ["Bye!", "Farewell", "Goodbye!", "Until we meet again.", "My people will talk to your people.",
           'до свидания товарищ']
error_resp = ["I'm not feeling too well... You might have to ask me later.",
              "Something went wrong... Try again?"]
user_goodbye = ["q", "quit", "bye", "goodbye", "thank you", "thanks", "yeet"]


def ask(query):
    if query.lower() in user_goodbye:
        return StaciaMsg("END", random.choice(goodbye))
    try:
        aid, conf, variables = classify(query)
        logging.info(variables)
        logging.info(f"{answers[aid]} -> {conf}")
        if conf < 0.05:
            return StaciaMsg("UNKNOWN", random.choice(no_answer))
        matched = match_to_variables(aid, variables)
        logging.info(matched)
        if matched is None:
            if len(variables) == 0:
                return StaciaMsg("UNKNOWN", random.choice(outside_domain))
            return StaciaMsg("UNKNOWN", random.choice(not_enough_info))
        answer = ans(aid, matched)
        return StaciaMsg("NORMAL", answer)
    except Exception as e:
        logging.error(e)
        return StaciaMsg("ERROR", random.choice(error_resp))


def greet():
    return random.choice(greetings)
