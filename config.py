import os
basedir = os.path.abspath(os.path.dirname(__file__))

# database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'roodkapje.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

ANNOTATION_DIR = os.path.join(basedir, "annotations")