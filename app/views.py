import codecs
import glob
import os
import json

from collections import Counter

import flask
from flask.ext.login import login_user, current_user, login_required

from app import app, lm, db
from models import User, Story
from forms import LoginForm, RegisterForm


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    flask.g.user = current_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.g.user is not None and flask.g.user.is_authenticated():
        return flask.redirect(flask.url_for("index"))
    form = LoginForm()
    if flask.request.method == 'GET':
        return flask.render_template('login.html', title='Sign In', form=form)
    if form.validate_on_submit() and form.validate_fields():
        flask.session['remember_me'] = form.remember_me.data
        login_user(form.get_user(), remember=form.remember_me.data)
        return flask.redirect(flask.url_for("index"))
    return flask.render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if flask.request.method == 'GET':
        return flask.render_template('register.html', title='Sign In', form=form)
    if form.validate_on_submit() and form.validate_fields():
        user = User(username=form.username.data,
                    firstname=form.firstname.data,
                    surname=form.surname.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('register.html', title='Sign Up', form=form)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = flask.g.user
    n_to_do = len(Story.query.filter_by(done=0).all())
    if n_to_do == 0:
        return flask.render_template('rainbows.html')
    story = Story.query.filter_by(user_id=user.id, done=0).first()
    if story is None:
        story = Story.query.filter_by(user_id=None, done=0).first()
        if story is None:
            return flask.render_template('index.html', user=user, story=None, to_do=n_to_do)
        story.user_id = user.id
        db.session.commit()
    return flask.render_template('index.html', user=user, story=story, to_do=n_to_do)

@app.route('/annotate/<storyname>', methods=['GET', 'POST'])
@login_required
def annotate(storyname):
    story = Story.query.filter_by(storyname=storyname).first()
    if flask.request.method == 'POST':
        answers = flask.request.json
        story.story = answers['story']
        story.done = 1
        db.session.commit()
        with codecs.open(os.path.join(app.config['ANNOTATION_DIR'], story.storyname + '.ann'), 'w', 'utf-8') as outfile:
            for qnumber, answer in sorted(answers['answers'].iteritems(), key=lambda i: int(i[0])):
                outfile.write("%s;%s\n" % (qnumber, answer))
        return json.dumps({'annotation stored':'OK'})
    with codecs.open(os.path.join(app.config["ROOT_DIR"], 'questions.json'), encoding='utf-8') as inf:
        questions = json.load(inf)
    return flask.render_template('annotate.html', questions=questions, story=story)

@app.route('/administration', methods=['GET', 'POST'])
@login_required
def administration():
    active_users = {u.id: u.firstname + ' ' + u.surname for u in User.query.all()}
    stories = ((i, s.storyname, 'ja' if s.done else 'nee', active_users[s.user_id] if s.user_id != None else 'Not Assigned')
               for i, s in enumerate(Story.query.all(), 1))
    return flask.render_template("administration.html", stories=stories, user=flask.g.user)

@app.route('/unlock', methods=['GET', 'POST'])
@login_required
def unlock():
    if flask.request.method == 'POST':
        stories_to_unlock = flask.request.json
        for story in stories_to_unlock:
            story = Story.query.filter_by(storyname=story).first()
            story.user_id = None
        db.session.commit()
    return json.dumps({"url": flask.url_for("administration")})

@app.route('/review/<storyname>', methods=['GET', 'POST'])
@login_required
def review(storyname):
    story = Story.query.filter_by(storyname=storyname, done=1).first()
    if story is None:
        return flask.render_template('404.html'), 404
    if flask.request.method == 'POST':
        answers = flask.request.json
        story.story = answers['story']
        db.session.commit()
        with codecs.open(os.path.join(app.config['ANNOTATION_DIR'], story.storyname + '.ann'), 'w', 'utf-8') as outfile:
            for qnumber, answer in sorted(answers['answers'].iteritems(), key=lambda i: int(i[0])):
                outfile.write("%s;%s\n" % (qnumber, answer))
        return json.dumps({'annotation stored':'OK'})
    with codecs.open(os.path.join(app.config["ROOT_DIR"], 'questions.json'), encoding='utf-8') as inf:
        questions = json.load(inf)
    with codecs.open(os.path.join(app.config['ANNOTATION_DIR'], story.storyname + '.ann'), encoding='utf-8') as inf:
        answers = {}
        for line in inf:
            qnumber, answer = line.strip().split(';', 1)
            answers[qnumber] = answer
    return flask.render_template('review.html', questions=questions, story=story, answers=answers)

@app.route('/graphs', methods=['GET'])
@login_required
def graphs():
    questions = {}
    for story in glob.glob(os.path.join(app.config['ANNOTATION_DIR'], '*.ann')):
        for line in codecs.open(story, encoding='utf-8'):
            qnumber, answers = line.strip().split(';', 1)
            answers = [answer.strip() for answer in answers.split(',')]
            if qnumber not in questions:
                questions[qnumber] = Counter()
            for answer in answers:
                questions[qnumber][answer] += 1
    for question, counts in questions.items():
        questions[question] = [{'label': answer, 'count': count} for answer, count in counts.items()]
    with codecs.open(os.path.join(app.config["ROOT_DIR"], 'questions.json'), encoding='utf-8') as inf:
        qnumbers = [(q['number'], q['question']) for q in json.load(inf)]
    return flask.render_template("graphs.html", questions=questions, numbers = qnumbers)

@app.errorhandler(404)
def not_found_error(error):
    return flask.render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return flask.render_template('500.html'), 500
