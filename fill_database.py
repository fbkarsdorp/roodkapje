import codecs
import os
from app import db, models

# first add the administrator
admin = models.User(username='admin', firstname='admin', surname='admin', password='admin')
db.session.add(admin)

# next add all participants
for user in open("users.txt"):
    username, name, password = user.strip().split(',')
    firstname, surname = name.split(' ', 1)
    user = models.User(username=username, 
                       firstname=firstname, surname=surname,
                       password=password)
    db.session.add(user)
db.session.commit()

# add all stories to the database (admin is author)
for directory in os.listdir('../../corpus'):
    if os.path.isdir(os.path.join('../../corpus', directory)):
        storyid = directory
        if 'transcription.txt' in os.listdir(os.path.join('../../corpus', directory)):
            print directory
            with codecs.open(os.path.join('../../corpus', directory, 'transcription.txt'), encoding='utf-8') as f:
                story = f.read()
                story = models.Story(storyname=storyid, story=story, done=0)
                db.session.add(story)

db.session.commit()

