#!/usr/bin/env python3
import csv
import logging
import re
import warnings
from nltk.tokenize import word_tokenize
from nltk import ngrams


import pandas as pd

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    from fuzzywuzzy import process, fuzz

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


def main():
    rd = RelevanceDetector(questions_src="questions.tsv")
    while True:
        query = input("Enter a query: ")
        rd.extract_variables(query)
        # results = rd.identify_variable(query)
        # print("Result: ", rd.__reduce_course(query, results).to_string)


class RelevanceDetector:
    def __init__(self, min_query_match=95, min_var_match=70, questions_src=None):
        self.min_query_match = min_query_match
        self.min_var_match = min_var_match

        if questions_src:
            self.load_questions(questions_src)
        else:
            self.questions = None

        self.syn_table = load_synonym_table()

    def predict(self, query):
        logging.debug(f"Received query: {query}")
        fuzzymatch = process.extractBests(query, choices=self.questions, processor=Question.processor,
                                          score_cutoff=self.min_query_match)
        logging.debug(f"Fuzzy match results: {fuzzymatch}")
        variables = self.__read_variables(query)
        logging.debug(f"Variables: {variables}")
        cleaned = self.__drop_variables(query, variables)
        logging.debug(f"Dropped variables: {cleaned}")
        logging.info(f"Predicting {query} -> {fuzzymatch[0]}")
        return fuzzymatch[0][0]

    def load_questions(self, file):
        questions = []
        with open(file) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter='\t')
            count = 0
            for row in csv_reader:
                count = count + 1
                questions.append(Question(row['question'],
                                          Answer(row['answerId'],
                                                 row['primary'],
                                                 row['secondary'])))
            logging.debug(f"Retrieved {count} questions.")
        self.questions = questions
        return self

    @staticmethod
    def __read_variables(query):
        res = re.search(r"\[.*?\]", query)
        return res.group() if res else []

    @staticmethod
    def __drop_variables(query, variables):
        q = query
        for var in variables:
            q = q.replace(var, '')
        return q

    @staticmethod
    def __fuzzy_query(query):
        return lambda row: fuzz.token_sort_ratio(query, row['synon'])

    def identify_variable(self, query, table=None):
        table = self.syn_table if table is None else table
        matches = table[table.apply(self.__fuzzy_query(query), axis=1) > self.min_var_match]
        return pd.DataFrame(matches)

    def __reduce_course(self, query):
        for noise in ['stat']:
            query = query.replace(noise, '')
        logging.debug(f"Reduced course to \"{query}\"")
        return self.identify_variable(query, self.syn_table)

    def extract_variables(self, query):
        q_words = word_tokenize(query)
        results = {}
        for n in range(1,min(len(q_words), 5)):
            n_grams = [" ".join(ngram) for ngram in ngrams(q_words, n)]
            for n_gram in n_grams:
                results[n_gram] = self.identify_variable(n_gram)
        [print(key+":", value) for key, value in results.items() if len(value) > 0]

class Question:
    def __init__(self, text, answer):
        self.text = text
        self.answer = answer

    def __repr__(self):
        return f"{self.text} -> {self.answer.primary}"

    @staticmethod
    def processor(question):
        return question.text


class Answer:
    def __init__(self, aid, primary, secondary=None):
        self.id = aid
        self.primary = primary
        self.secondary = secondary



if __name__ == "__main__":
    main()
