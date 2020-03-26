from flask import Flask
from flask_pymongo import PyMongo
from config import Config


app = Flask(__name__)
app.config.from_object(Config)


from app import routes
