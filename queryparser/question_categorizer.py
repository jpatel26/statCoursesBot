import string
import warnings

import nltk
from loader import load_synonym_table, load_questions
from nltk.stem import PorterStemmer
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


lemmatizer = nltk.stem.WordNetLemmatizer
ps = PorterStemmer()

syn_table = load_synonym_table()
syn_entries = syn_table['synon']  # Documents
syn_labels = syn_table['can']  # Labels

question_df = load_questions()
question_entries = question_df['question']  # Documents
question_labels = question_df['answerId']  # Label type 1

remove_punct_dict = {ord(punct): None for punct in string.punctuation}


def stem_tokens(tokens):
    return [ps.stem(token) for token in tokens]


def stem_normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


def is_variable(word):
    return word.startswith('[') and word.endswith(']')


def question_stem_normalize(text):
    return stem_tokens(
        [word for word in nltk.word_tokenize(text.lower().translate(remove_punct_dict)) if not is_variable(word)])


class TfidfClassifier:
    def __init__(self, tokenizer=stem_normalize, stop_words=None, ngram_range=(1, 3)):
        self.tokenizer = tokenizer
        self.stop_words = stop_words
        self.ngram_range = ngram_range
        self.model = TfidfVectorizer(tokenizer=self.tokenizer, stop_words=self.stop_words, ngram_range=self.ngram_range)
        self.tfidf = None
        self.labels = None

    def fit_transform(self, X, Y):
        self.tfidf = self.model.fit_transform(X)
        self.labels = Y

    def predict(self, Y):
        vec = self.model.transform(Y)
        similarity = cosine_similarity(vec, self.tfidf)
        idx = similarity.argsort()[0][-1]
        flat = similarity.flatten()
        flat.sort()
        req_tfidf = flat[-1]
        return self.labels[idx], req_tfidf


tfSynClassifier = TfidfClassifier(stop_words='english')
tfSynClassifier.fit_transform(syn_entries, syn_labels)

tfQuestionClassifier = TfidfClassifier(tokenizer=question_stem_normalize)
tfQuestionClassifier.fit_transform(question_entries, question_entries)


def respond(query):
    y, conf = tfSynClassifier.predict([query])
    print(y)
    y, conf = tfQuestionClassifier.predict([query])
    print(y)
    if conf == 0:
        return "Sorry, I don't understand"
    else:
        return y


if __name__ == "__main__":
    # print(tfSynClassifier.model.vocabulary_)
    # print(tfQuestionClassifier.model.vocabulary_)
    while True:
        user_response = input("Give me a query: ")
        if user_response == "q":
            exit(0)
        print(respond(user_response))
