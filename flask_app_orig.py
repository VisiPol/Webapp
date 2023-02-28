
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://prashanthmac:Summer_2023@prashanthmac.mysql.pythonanywhere-services.com/prashanthmac$defaul".format(
    username="prashanthmac",
    password="Summer_2023",
    hostname="prashanthmac.mysql.pythonanywhere-services.com",
    databasename="prashanthmac$default",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

