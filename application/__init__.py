from flask import Flask
from config import Config
from flask_mongoengine import MongoEngine
from flask_restplus import Api
from pymongo import MongoClient

api = Api()

app = Flask(__name__)
app.config.from_object(Config)

# cluster = MongoClient("mongodb+srv://pawan7016:Pawan60%40@cluster0.mrbvi.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
# db = cluster["Voting"]
db = MongoEngine()
db.init_app(app)
api.init_app(app)

from application import routes

