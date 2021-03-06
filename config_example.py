import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    TEMPLATES_AUTO_RELOAD = True
    MONGO_URI = 'mongodb://localhost:27017/essentialstracker'
    MONGO_DBNAME = 'essentialstracker'
