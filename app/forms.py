from flask_wtf import Form
from wtforms import StringField, TextAreaField, Field, PasswordField, BooleanField, RadioField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired
from .models import User

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def validate_fields(self):
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

class RegisterForm(Form):
    username = StringField('username', validators=[DataRequired()])
    firstname = StringField('Voornaam', validators=[DataRequired()])
    surname = StringField('Achternaam', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    cpassword = PasswordField('confirm password', validators=[DataRequired()])

    def validate_fields(self):
        if not self.available_username():
            self.username.errors = ('Deze naam is bezet.',)
            return False
        if self.password.data != self.cpassword.data:
            self.cpassword.errors = ('Wachtwoorden zijn niet hetzelfde', )
            return False
        return True

    def available_username(self):
        return User.query.filter_by(username=self.username.data).first() is None


class SectionField(Field):
    pass

class StoryForm(Form):
    story = TextAreaField("story", widget=TextArea())

class RadioQuestionForm(Form):
    question = RadioField(label="", choices=[], validators=[DataRequired()])