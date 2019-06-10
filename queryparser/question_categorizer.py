#!/usr/bin/env python3
import string
import warnings
from collections import namedtuple

import nltk
from loader import load_synonym_table, load_questions
from nltk.stem import PorterStemmer, WordNetLemmatizer

warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics.classification import accuracy_score
from nltk.corpus import stopwords as _sw
from scipy.stats import entropy

lemmatizer = nltk.stem.WordNetLemmatizer
stopwords = _sw.words('english')
ps = PorterStemmer()
lm = WordNetLemmatizer()

syn_table = load_synonym_table()
syn_entries = syn_table['synon']  # Documents
Synonym = namedtuple('Synonym', 'table column canon')
syn_labels = [Synonym(row[1], row[2], row[3]) for row in syn_table.itertuples()]  # Labels

question_df = load_questions()
question_entries = question_df['question']  # Documents
question_labels = question_df['answerId']  # Label type 1

punct_dict = {ord(punct): None for punct in string.punctuation}


def stem_tokens(tokens):
    return [ps.stem(token) for token in tokens]


def lemmatize_tokens(tokens):
    return [lm.lemmatize(token) for token in tokens]


def reduce_tokens(tokens, reducer=stem_tokens):
    return reducer(tokens)


def translated_tokens(text):
    return nltk.word_tokenize(text.lower().translate(punct_dict))


def stem_normalize(text):
    return lemmatize_tokens(translated_tokens(text))


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
        # print(precision_recall_fscore_support(Y_test, Y_pred))
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
        srt = [entry for entry in srt if entry[1] > 0]
        return srt

    def label_of(self, index):
        if self.label_extractor is not None:
            return self.label_extractor(self.labels, index)
        return self.labels[index]


def row_extractor(df, idx):
    return df.loc[idx, :]


tfSynClassifier = TfidfClassifier(stop_words='english', analyzer='char_wb', ngram_range=(4, 5))
tfSynClassifier.fit_transform(syn_entries, syn_labels)
# tfSynClassifier.train_and_evaluate(syn_entries, syn_labels)

tfQuestionClassifier = TfidfClassifier(tokenizer=question_stem_normalize)
tfQuestionClassifier.fit_transform(question_entries, question_entries)

variable_to_col = {
    '[STAT-COURSE]': 'course_num',
    '[COURSE-LIST]': 'course_num',
    '[TOPIC]': 'course_num',
    '[STAT-FACULTY]': 'faculty_last_name',
    '[ROOM]': 'course_room',
    '[COURSE-NUMBER]': 'course_num',
    '[TERM]': 'term',
    '[COURSE-TITLE]': 'course_num'
    # [COURSE-LEVEL]
    # NUM_RATING
}

non_starters = ['statistical']
non_starters.extend(stopwords)


def variable_scan(classifier, query, is_exclusive=True, is_relevant=(lambda x: True)):
    variables = []
    words = nltk.word_tokenize(query)
    tagged = nltk.pos_tag(words)
    print(tagged)
    i = -1
    while i < len(words) - 1:
        i = i + 1
        if words[i] in non_starters: continue
        results = classifier.predict_take_all(words[i])
        if len(results) == 0 or results[0][1] < 0.2: continue
        j = i + 1
        while j < len(words) - 1:
            j = j + 1
            if words[j - 1] in ['.', ',']:
                break
            next = classifier.predict_take_all(" ".join(words[i:j]))
            if next[0][1] > 0.90:
                # End due to certainty
                results = next
                break
            if sum_matching(next) < sum_matching(results):
                # End due to die-off
                break
            results = next
        results = [res for res in results if is_relevant(res)]
        if len(results):
            variables.append(results[0])
            # Found something and flag is on
            if is_exclusive:
                i = j
    return variables


def variable_scan2(classifier, query, is_exclusive=True, is_relevant=(lambda x: True)):
    V = []
    W = [word.lower() for word in nltk.word_tokenize(query)]
    i = -1
    while i < len(W) - 1:
        i = i + 1
        if W[i] in stopwords or W[i] in string.punctuation:
            continue
        _, sim = classifier.predict(W[i])
        if sim < 0.2: continue
        j = find_end(W, i)
        prev_matches = classifier.predict_take_all(' '.join(W[i:j]))
        prev_ent = result_entropy(prev_matches) * 1.015 ** (i - j)
        j = j - 1
        while j > i:
            print(' '.join(W[i: j]))
            this_match = classifier.predict_take_all(' '.join(W[i: j]))
            this_ent = result_entropy(this_match) * 1.015 ** (i - j)
            if this_ent > prev_ent:
                break
            prev_matches = this_match
            prev_ent = this_ent
            j = j - 1
        results = [res for res in prev_matches if is_relevant(res)]
        if len(results):
            V.append(results[0])
            if is_exclusive:
                i = j
    return V


def find_end(W, i):
    j = i + 1
    while j < len(W) and W[j] not in ['.', ',']:
        j = j + 1
    return j


def result_entropy(matching):
    return entropy([conf for _, conf in matching])


def sum_matching(matching):
    return sum([conf for _, conf in matching])


def avg_matching(matching):
    return sum_matching(matching) \
           / sum([1 for _, conf in matching if conf > 0])


def get_query_vars(question):
    return [var for var in variable_to_col if var in question]


def is_relevant_col(columns, minsim=0.25):
    return lambda row: row[0].column in columns and row[1] > minsim

def meets_minsim(minsim=0.25):
    return lambda row[1] > minsim


def remove_variables(query, variables, min_conf=0.7, limit=None):
    limit = limit if limit is not None else len(variables)
    var_filter = []
    for entry in variables[:limit]:
        var, _, conf = entry
        if conf > min_conf:
            [var_filter.append(word)  # Add a translation entry
             for word in nltk.word_tokenize(var)  # ... from the words
             if word not in stopwords]  # But keep stop words (because they matter)
    var_filter = set(var_filter)
    reduced = [word for word in nltk.word_tokenize(query) if word.lower() not in var_filter]
    return " ".join(reduced)


def columns_in_use(question):
    question_vars = get_query_vars(question)
    return [variable_to_col[qvar] for qvar in question_vars]


def respond(query):
    y, sim = tfQuestionClassifier.predict(query)
    columns = columns_in_use(y)
    variables = variable_scan(tfSynClassifier, query, is_relevant=is_relevant_col(columns))
    print("Relevant variables(as canon) from user question:\n",
          [var.canon for var, _ in variables if var.column in columns])
    print(sim)
    if sim == 0:
        return "Sorry, I don't think I can answer that..."
    else:
        return y


if __name__ == "__main__":
    print(respond("When can I take inference for management i?"))
    print(respond("Can I take inference for management ii before i take inference for management i?"))
    print(respond("What order can I take stat 312, stat 542, and statistical computing with r in?"))
    while True:
        user_response = input("Give me a query: ")
        if user_response == "q":
            exit(0)

        print(respond(user_response))
