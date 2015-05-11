import codecs
import os
import json

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
    story = Story.query.filter_by(user_id=user.id, done=0).first()
    if story is None:
        story = Story.query.filter_by(user_id=None, done=0).first()
        story.user_id = user.id
        db.session.commit()
    n_to_do = len(Story.query.filter_by(done=0).all())
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

@app.errorhandler(404)
def not_found_error(error):
    return flask.render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return flask.render_template('500.html'), 500
