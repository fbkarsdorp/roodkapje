import os
basedir = os.path.abspath(os.path.dirname(__file__))

# database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'annotations.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

ANNOTATION_DIR = os.path.join(basedir, "annotations")
if not os.path.isdir(ANNOTATION_DIR):
    os.mkdir(ANNOTATION_DIR)
ROOT_DIR = basedir