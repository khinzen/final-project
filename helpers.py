import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

import pandas as pd

sia = SentimentIntensityAnalyzer()

def sent_score(prompt):

    sent_tokens = nltk.sent_tokenize(prompt)

    scores = []

    for sent in sent_tokens:

        scores.append(sia.polarity_scores(sent))

    df = pd.DataFrame.from_dict(scores)

    return df

def posneg(df, prompt):

    sent_tokens = nltk.sent_tokenize(prompt)

    most_pos_ind = df['pos'].idxmax()
    most_neg_ind = df['neg'].idxmax()

    most_pos_sent = sent_tokens[most_pos_ind]
    most_neg_sent = sent_tokens[most_neg_ind]

    return most_pos_sent, most_neg_sent

# test = sent_score("Hello, my name is Krishan. I am in CLPS 0950. My favorite dog is my own. I walked a goat last weekend.")

# pos, neg = posneg(test, "Hello, my name is Krishan. I am in CLPS 0950. My favorite dog is my own. I walked a goat last weekend.")

# print(pos, neg)