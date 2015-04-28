import codecs
import os
from flask.ext.wtf import Form
from wtforms import RadioField, StringField, TextAreaField, Field, PasswordField, BooleanField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired
from app import app
from models import User
from utils import SectionCounter

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def validate_on_submit(self):
        user = self.get_user()
        if user is None:
            self.username.errors = ('Jij bestaat niet.',)
            return False
        if user.password != self.password.data:
            self.password.errors = ('Verkeerd wachtwoord.',)
            return False
        return True

    def get_user(self):
        return User.query.filter_by(username=self.username.data).first()


class SectionField(Field):
    pass

class QuestionForm(Form):
    story = TextAreaField("story", widget=TextArea())
    sc = SectionCounter()
    for k, line in enumerate(codecs.open(os.path.join(app.config["ROOT_DIR"], "schema.md"), encoding='utf-8')):
        fields = line.strip().split('\t')
        if len(fields) > 1:
            qnumber = sc.to_number(fields[0])
        if len(fields) <= 1:
            continue
        elif len(fields) == 2:
            question = SectionField(label="<h%s>%s</h%s>" % (fields[0].count('#'), fields[1], fields[0].count('#')))
        elif fields[1] == 'B':
            question = RadioField(label="%s" % fields[2], choices=[('y', 'ja'), ('n', 'nee')], validators=[DataRequired()])
            question.type = 'B'
        elif fields[1] == 'R':
            choices = fields[3].split(',')
            question = RadioField(label="%s" % fields[2], choices=[(f, f) for i, f in enumerate(fields[3].split(','))], validators=[DataRequired()])
        elif fields[1] == 'T':
            question = StringField(label="%s" % fields[2], validators=[DataRequired()])
        else:
            raise ValueError()
        question.qnumber = qnumber
        setattr(Form, qnumber, question)

    def validate_answers(self):
        return True
