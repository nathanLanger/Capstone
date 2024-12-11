import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

tweets = pd.read_csv('socialmedia-disaster-tweets-DFE.csv',encoding='latin1')[['text','choose_one']]
tweets.columns = ['tweet','class']
tweets = tweets[(tweets['class'] == 'Relevant') | (tweets['class'] == 'Not Relevant')]
tweets = tweets.reset_index(drop=True)
tweets.tail()

#1. Remove any html and emoticons
import re
def preprocessor(text):
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
    text = re.sub('[\W]+', ' ', text.lower()) +\
        ' '.join(emoticons).replace('-', '')
    return text
preprocessor("</a>This :) is :( a test :-)!")
tweets['tweet'] = tweets['tweet'].apply(preprocessor)

#2. Reindex
import numpy as np

tweets = tweets.reindex(np.random.permutation(tweets.index))

print(tweets.head())
print(tweets.tail())

#3 and #4. Stopwords
import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords

stop = stopwords.words('english')
stop = stop + [u'a',u'b',u'c',u'd',u'e',u'f',u'g',u'h',u'i',u'j',u'k',u'l',u'm',u'n',u'o',u'p',u'q',u'r',u's',u't',u'v',u'w',u'x',u'y',u'z']

import nltk
nltk.download('wordnet')
def split_into_lemmas(tweet):
    tweet = str(tweet).lower()
    words = TextBlob(tweet).words
    # for each word, take its "base form" = lemma
    return [word.lemma for word in words if word not in stop]

tweets.tweet.head().apply(split_into_lemmas)

#5
tweets_bow = bow_transformer.transform(tweets['tweet'])
print('sparse matrix shape:', tweets_bow.shape)
print('number of non-zeros:', tweets_bow.nnz)
print('sparsity: %.2f%%' % (100.0 * tweets_bow.nnz / (tweets_bow.shape[0] * tweets_bow.shape[1])))

tweets_bow_train = tweets_bow[:8000]
tweets_bow_test = tweets_bow[8000:]
tweets_class_train = tweets['class'][:8000]
tweets_class_test = tweets['class'][8000:]

print(tweets_bow_train.shape)
print(tweets_bow_test.shape)

#6.
tweets_class = MultinomialNB().fit(tweets_bow_train, tweets_class_train)

predictions = tweets_class.predict(tweets_bow_test)

print(classification_report(tweets_class_test, predictions))

#7.
def predict_tweet(new_tweet):
    new_sample = bow_transformer.transform([new_tweet])
    print(new_tweet, np.around(tweets_class.predict_proba(new_sample), decimals=5),"\n")

predict_review('This burger is very tasty!')
predict_review('I am sick and tired of my program not giving me a bad prediction!')