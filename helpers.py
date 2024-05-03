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

def overall_sentiment(df):

    sentiment = {}

    sentiment[1] = len(df[df['compound'] > 0.333])
    sentiment[2] = len(df.loc[(df['compound'] < 0.333) & (df['compound'] > -0.333)])
    sentiment[3] = len(df[df['compound'] < -0.333])

    overall_sent = 0
    for key in sentiment:
        if sentiment[key] >= overall_sent:
            overall_sent = key
    
    return overall_sent

test = sent_score("Hello, my name is Krishan. I am in CLPS 0950. My favorite dog is my own. I walked a goat last weekend. I love life.")
sent = overall_sentiment(test)

# pos, neg = posneg(test, "Hello, my name is Krishan. I am in CLPS 0950. My favorite dog is my own. I walked a goat last weekend.")

# print(pos, neg)