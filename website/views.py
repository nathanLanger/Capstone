from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from .models import Business
from . import db
import json

import sys
import os
# Go two dirs up
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from algorithm import Model

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

@views.route('msb', methods=['GET', 'POST'])
def msb():
    if request.method == 'POST': 
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        bname = request.form.get('bname')
        email = request.form.get('email')
        #newb = Business(data=bname, user_id=current_user.id)
        #db.session.add(newb)
        #db.session.commit()
        flash('Data Received', category='success')
        input = str(bname)
        output = Model(input).output
        output.sort(reverse=True)
    else:
        output = ['Please Enter Info']
    return render_template("msb.html", user=current_user, output=output)#, output=alg_output)   #takes output

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