import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import glob
import os
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB

#for step 4
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop = stopwords.words('english')
stop = stop + [u'a',u'b',u'c',u'd',u'e',u'f',u'g',u'h',u'i',u'j',u'k',u'l',u'm',u'n',u'o',u'p',u'q',u'r',u's',u't',u'v',u'w',u'x',u'y',u'z']
import nltk
nltk.download('wordnet')

#for step 2
import re
def preprocessor(text):
    if not isinstance(text, str):   #checks for NaN data
        return ''
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
    text = re.sub('[\W]+', ' ', text.lower()) +\
        ' '.join(emoticons).replace('-', '')
    return text
    """ print(preprocessor("</a>This :) is :( a test :-)!"))
    print(entries['entry']) """      

class Model(object):
    output = []
    def __init__(self, input):
        #2*
         
        #1. Get most recent data
        def get_most_recent_download(save_folder):
            files = glob.glob(save_folder + '/*')
            max_file = max(files, key=os.path.getctime)
            filename = max_file
            return filename
        filename = get_most_recent_download('downloads')
        #print(filename)
        # All data at disposal
        """ entries = pd.read_csv(filename, encoding='latin1')[['LEGAL NAME','DBA NAME','STREET ADDRESS','CITY',
                                                        'STATE','ZIP','MSB ACTIVITIES','STATES OF MSB ACTIVITIES',
                                                        'ALL STATES & TERRITORIES & FOREIGN FLAG**','FOREIGN LOCATION',
                                                        '# OF BRANCHES','AUTH SIGN DATE','RECEIVED DATE']]
        entries.columns = ['LEGAL NAME','DBA NAME','STREET ADDRESS','CITY',
                        'STATE','ZIP','MSB ACTIVITIES','STATES OF MSB ACTIVITIES',
                        'ALL STATES & TERRITORIES & FOREIGN FLAG**','FOREIGN LOCATION',
                        '# OF BRANCHES','AUTH SIGN DATE','RECEIVED DATE'] """
        # Make a list from 'MSB ACTIVITIES' column - to select
        # Choices of data - 'DBA NAME' is entry, 'MSB ACTIVITIES' is class
        entries = pd.read_csv(filename, encoding='latin1')[['DBA NAME', 'MSB ACTIVITIES']]
        entries.columns = ['entry', 'class']

        # Also remove rows with NaN values in 'MSB Activities' class
        entries = entries.dropna(subset=['class'])

        # Record all options
        msb_options = set()
        for eachs in entries['class']:
            list = str(eachs).split(' ')
            for each in list:
                if each != 'nan':
                    msb_options.add(each)

        for msb_option in msb_options:
            print(msb_option)
            # 1. Reload Data
            entries = pd.read_csv(filename, encoding='latin1')[['DBA NAME', 'MSB ACTIVITIES']]
            entries.columns = ['entry', 'class']
            #entries = entries[(entries['class'] == '405') | (entries['class'] == '408')] results in just two classes
            #entries = entries[entries['class'].str.contains('405', na=False)] results in all the classes
            entries = entries[(entries['class'] == (lambda x: msb_option in x)) | (entries['class'] != (lambda x: msb_option in x))]
            entries = entries.reset_index(drop=True)
            """ print(entries.tail()) """

            #2. Remove any html and emoticons from 'DBA NAME' entry
            entries['entry'] = entries['entry'].apply(preprocessor)

            # Make it Binary data
            for i in range(0,len(entries['class'])):
                if str(msb_option) in str(entries['class'][i]):
                    entries.at[i, 'class'] = 'True'
                else:
                    entries.at[i, 'class'] = 'False'

            #3. Reindex
            import numpy as np

            entries = entries.reindex(np.random.permutation(entries.index))

            """ print(entries.head())
            print(entries.tail()) """

            #4*. Stopwords
            def split_into_lemmas(entry):
                entry = str(entry).lower()
                words = TextBlob(entry).words
                # for each word, take its "base form" = lemma
                return [word.lemma for word in words if word not in stop]

            entries.entry.head().apply(split_into_lemmas)

            #5.
            bow_transformer = CountVectorizer(analyzer=split_into_lemmas).fit(entries['entry'])
            #print(len(bow_transformer.vocabulary_))

            #6.
            entries_bow = bow_transformer.transform(entries['entry'])
            """ print('sparse matrix shape:', entries_bow.shape)
            print('number of non-zeros:', entries_bow.nnz)
            print('sparsity: %.2f%%' % (100.0 * entries_bow.nnz / (entries_bow.shape[0] * entries_bow.shape[1]))) """

            # Get the size of entries and factor into test size
            rows, columns = entries.shape
            train_allocation = int(.8 * rows)
            entries_bow_train = entries_bow[:train_allocation]
            entries_bow_test = entries_bow[train_allocation:]
            entries_class_train = entries['class'][:train_allocation]
            entries_class_test = entries['class'][train_allocation:]

            """ print(entries_bow_train.shape)
            print(entries_bow_test.shape) """

            #7. 
            entries_class = MultinomialNB().fit(entries_bow_train, entries_class_train)

            predictions = entries_class.predict(entries_bow_test)

            # print(classification_report(entries_class_test, predictions))

            #8. 
            def predict_entry(new_entry):
                new_sample = bow_transformer.transform([new_entry])
                result = str(np.around(entries_class.predict_proba(new_sample), decimals=5))
                #remove bracket, keep the prob True, float, rounded 2 places after decimal, *100, and str
                result = str(float("{:.2f}".format(float((result[2:]).split(' ', 1)[0])*100)))
                return('There is a '+ result + ' percent chance '+ str(msb_option) + ' is right for you!')
                #print(new_entry, np.around(entries_class.predict_proba(new_sample), decimals=5),"\n")

            input = ''
            self.output.append(predict_entry(input))
            
        #9. Sort the output by probabilities reported
        def extract_first_number(string):
            # Use regex to find the first number in the string
            match = re.search(r'\d+', string)
            return int(match.group()) if match else 0  # Return the number, or 0 if no number is found

        # Sort the strings based on the first number, from largest to smallest
        self.output = sorted(self.output, key=extract_first_number, reverse=True)