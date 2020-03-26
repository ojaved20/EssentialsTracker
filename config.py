import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    TEMPLATES_AUTO_RELOAD = True
    MONGO_URI = 'mongodb+srv://ojaved:mViolin09!@cluster0-fkbd0.mongodb.net/essentialstracker?retryWrites=true&w=majority'
    MONGO_DBNAME = 'essentialstracker'
