from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from .models import Business
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

output = ''
email = ''
bname = ''
email = ''
@views.route('msb', methods=['GET', 'POST'])
def msb():
    if request.method == 'POST': 
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        global email
        global bname
        bname = request.form.get('bname')
        email = request.form.get('email')
        #newb = Business(data=bname, user_id=current_user.id)
        #db.session.add(newb)
        #db.session.commit()
        flash('Data Received', category='success')
        get_output()

    return render_template("msb.html", user=current_user)

@views.route('meet', methods=['GET', 'POST'])
def meet():
    return render_template("meet.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

def get_output():
    import pandas as pd
    import numpy as np
    from textblob import TextBlob
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    import glob
    import os
    from website.views import bname

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
    #entries = entries[(entries['class'] == '405') | (entries['class'] == '408')] results in just two classes
    #entries = entries[entries['class'].str.contains('405', na=False)] results in all the classes
    entries = entries[(entries['class'] == (lambda x: '405' in x)) | (entries['class'] != (lambda x: '405' in x))]
    entries = entries.reset_index(drop=True)
    """ print(entries.tail()) """

    #2. Remove any html and emoticons from 'DBA NAME' entry
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
    entries['entry'] = entries['entry'].apply(preprocessor)

    # Also remove rows with NaN values in 'MSB Activities' class
    entries = entries.dropna(subset=['class'])
    # Make it Binary data
    for i in range(0,len(entries['class'])):
        if '405' in entries['class'][i]:
            entries.at[i, 'class'] = 'True'
        else:
            entries.at[i, 'class'] = 'False'

    #3. Reindex
    import numpy as np

    entries = entries.reindex(np.random.permutation(entries.index))

    """ print(entries.head())
    print(entries.tail()) """

    #4. Stopwords
    import nltk
    nltk.download('stopwords')

    from nltk.corpus import stopwords

    stop = stopwords.words('english')
    stop = stop + [u'a',u'b',u'c',u'd',u'e',u'f',u'g',u'h',u'i',u'j',u'k',u'l',u'm',u'n',u'o',u'p',u'q',u'r',u's',u't',u'v',u'w',u'x',u'y',u'z']

    import nltk
    nltk.download('wordnet')
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
    from sklearn.metrics import classification_report
    from sklearn.naive_bayes import MultinomialNB
    entries_class = MultinomialNB().fit(entries_bow_train, entries_class_train)

    predictions = entries_class.predict(entries_bow_test)

    #print(classification_report(entries_class_test, predictions))

    #8. 
    def predict_entry(new_entry):
        new_sample = bow_transformer.transform([new_entry])
        #print(new_entry, np.around(entries_class.predict_proba(new_sample), decimals=5),"\n")
        return entries_class.predict_proba(new_sample)

    # Submit an entry
    def submit(input):
        global output
        output = predict_entry(input)
        return output

    input = bname
    global output
    output = submit(input)

    import smtplib
    #SERVER = "localhost"

    FROM = 'BusinessRaccoon.com'

    global email
    TO = [email] # must be a list

    SUBJECT = "Here is the suggested msb activities for your MSB!"

    TEXT = output +""

    # Prepare actual message

    message = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the mail

    server = smtplib.SMTP('myserver')
    server.sendmail(FROM, TO, message)
    server.quit()