import codecs
import os
from app import db, models

# first add the administrator
admin = models.User(username='admin', firstname='admin', surname='admin', password='admin')
db.session.add(admin)
db.session.commit()

for filename in os.listdir('corpus'):
    if filename.endswith(".txt"):
        storyid = filename.replace(".txt", '')
        with codecs.open(os.path.join('corpus', filename), encoding='utf-8') as f:
            story = f.read()
            story = models.Story(storyname=storyid, story=story, done=0)
            db.session.add(story)

db.session.commit()

