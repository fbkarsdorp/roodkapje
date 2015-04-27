import flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = flask.Flask(__name__)
app.config.from_object('config')
app.secret_key = "=\x07BoZ\xeb\xb0\x13\x88\xf8mW(\x93}\xe6k\r\xebA\xbf\xff\xb1v"
db = SQLAlchemy(app)
lm = LoginManager()
lm.session_protection = 'strong'
lm.init_app(app)
lm.login_view = 'login'

from app import views, models