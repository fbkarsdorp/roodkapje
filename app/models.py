from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)
    firstname = db.Column(db.String(64), index=True, unique=False)
    surname = db.Column(db.String(64), index=True, unique=False)
    password = db.Column(db.String(64), index=True, unique=False)
    stories = db.relationship('Story', backref='annotator', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User(%r)>' % self.username

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    storyname = db.Column(db.String(64), index=True, unique=False)
    story = db.Column(db.String())
    done = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Story(%s, done=%s)>' % (self.storyname, self.done)
