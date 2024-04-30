import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

import matplotlib.pyplot as plt
import pandas as pd

sia = SentimentIntensityAnalyzer()

sample = "This is the best day ever. I am so very happy. Life is amazing."
sample2 = "On the other hand, altering an individual gene within the program may have a more localized effect, primarily affecting the function encoded by that specific gene without necessarily influencing the activity of other genes within the program. While this can still be significant, especially if the gene plays a critical role in the program, it may not have the same broad-reaching impact as altering a regulatory gene. Overall, targeting regulatory proteins provides a strategic approach to modulating the activity of gene programs and understanding the broader regulatory mechanisms that govern cellular processes."

tokens = nltk.word_tokenize(sample)
print(tokens[:])

tagged = nltk.pos_tag(tokens)
print(tagged)

print(sia.polarity_scores(sample))

sent_sample = nltk.sent_tokenize(sample)
sent_sample2 = nltk.sent_tokenize(sample)

results = []
for sent in range(len(sent_sample2)):
    results.append(sia.polarity_scores(sent_sample2[sent]))

df = pd.DataFrame.from_dict(results)

df['compound'].hist(bins=3)
